"""Kubernetes runtime reconciler for isolated Hermes instances."""

from __future__ import annotations

import asyncio
import re
import secrets
from typing import Any

from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.exceptions import ApiException

from ..config import Settings
from .runtime import RuntimeArtifact


def _name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]", "-", value.lower()).strip("-")
    return normalized[:63].rstrip("-")


class KubernetesProvider:
    kind = "kubernetes"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.apps: client.AppsV1Api | None = None
        self.core: client.CoreV1Api | None = None
        self.api_client: client.ApiClient | None = None

    async def start(self) -> None:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            await config.load_kube_config(context=self.settings.kubernetes_context or None)
        self.api_client = client.ApiClient()
        self.apps = client.AppsV1Api(self.api_client)
        self.core = client.CoreV1Api(self.api_client)

    async def close(self) -> None:
        if self.api_client:
            await self.api_client.close()

    def ready(self) -> bool:
        return self.apps is not None and self.core is not None

    def _apis(self) -> tuple[client.AppsV1Api, client.CoreV1Api]:
        if self.apps is None or self.core is None:
            raise RuntimeError("Kubernetes provider has not been started")
        return self.apps, self.core

    async def _apply(self, create: Any, patch: Any, name: str, namespace: str, body: Any) -> None:
        try:
            await create(namespace=namespace, body=body)
        except ApiException as exc:
            if exc.status != 409:
                raise
            await patch(name=name, namespace=namespace, body=body)

    async def provision(
        self,
        instance_id: str,
        image: str | None,
        runtime: dict[str, Any],
        labels: dict[str, str],
    ) -> RuntimeArtifact:
        apps, core = self._apis()
        image = image or runtime.get("image")
        if not image:
            raise RuntimeError("kubernetes runtimes require runtime.image or managedImageId")
        placement = runtime.get("kubernetes") or {}
        namespace = placement.get("namespace") or self.settings.runtime_namespace
        workload = _name(f"hermes-{instance_id}")
        service = workload
        pvc = f"{workload}-data"
        secret_name = f"{workload}-auth"
        selector = {"app.kubernetes.io/name": "hermes", "edith.io/instance-id": instance_id}
        gateway_token = secrets.token_urlsafe(48)
        auth_secret = client.V1Secret(
            metadata=client.V1ObjectMeta(name=secret_name, labels=selector),
            string_data={"gateway-token": gateway_token},
        )
        await self._apply(
            core.create_namespaced_secret,
            core.patch_namespaced_secret,
            secret_name,
            namespace,
            auth_secret,
        )
        claim = client.V1PersistentVolumeClaim(
            metadata=client.V1ObjectMeta(name=pvc, labels=selector),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                storage_class_name=placement.get("storageClassName")
                or self.settings.default_storage_class
                or None,
                resources=client.V1VolumeResourceRequirements(
                    requests={
                        "storage": str(
                            placement.get("persistentVolumeSize")
                            or self.settings.default_storage_size
                        )
                    }
                ),
            ),
        )
        await self._apply(
            core.create_namespaced_persistent_volume_claim,
            core.patch_namespaced_persistent_volume_claim,
            pvc,
            namespace,
            claim,
        )
        resource_spec = runtime.get("resources") or {}
        resource_requests = {
            "cpu": str(resource_spec.get("cpu", "500m")),
            "memory": str(resource_spec.get("memory", "1Gi")),
        }
        resource_limits = {
            "cpu": str(resource_spec.get("cpu", "2")),
            "memory": str(resource_spec.get("memory", "4Gi")),
        }
        if resource_spec.get("ephemeralStorage"):
            resource_requests["ephemeral-storage"] = str(resource_spec["ephemeralStorage"])
            resource_limits["ephemeral-storage"] = str(resource_spec["ephemeralStorage"])
        if resource_spec.get("gpu"):
            resource_limits["nvidia.com/gpu"] = str(resource_spec["gpu"])
        environment = [
            client.V1EnvVar(name="HERMES_HOME", value="/opt/data"),
            client.V1EnvVar(name="HOME", value="/opt/data"),
        ]
        for key, value in (runtime.get("environment") or {}).items():
            if "value" in value:
                environment.append(client.V1EnvVar(name=key, value=str(value["value"])))
            elif "secretRef" in value:
                reference = value["secretRef"]
                environment.append(
                    client.V1EnvVar(
                        name=key,
                        value_from=client.V1EnvVarSource(
                            secret_key_ref=client.V1SecretKeySelector(
                                name=reference["name"], key=reference.get("key") or key
                            )
                        ),
                    )
                )
        token_env = client.V1EnvVar(
            name="HERMES_SESSION_TOKEN",
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name=secret_name, key="gateway-token")
            ),
        )
        volume_mounts = [client.V1VolumeMount(name="data", mount_path="/opt/data")]
        volumes = [
            client.V1Volume(
                name="data",
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc),
            )
        ]
        for item in runtime.get("volumes") or []:
            volume_name = _name(str(item["name"]))
            if volume_name == "data":
                raise RuntimeError("The data volume name is reserved")
            source = item.get("source") or {}
            volume = client.V1Volume(name=volume_name)
            if source.get("persistentVolumeClaim"):
                volume.persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=str(source["persistentVolumeClaim"])
                )
            elif source.get("hostPath"):
                volume.host_path = client.V1HostPathVolumeSource(path=str(source["hostPath"]))
            elif source.get("emptyDir"):
                volume.empty_dir = client.V1EmptyDirVolumeSource()
            else:
                raise RuntimeError(f"Volume {item['name']} has no supported source")
            volumes.append(volume)
            volume_mounts.append(
                client.V1VolumeMount(
                    name=volume_name,
                    mount_path=str(item["mountPath"]),
                    read_only=bool(item.get("readOnly", False)),
                )
            )
        hermes = client.V1Container(
            name="hermes",
            image=image,
            image_pull_policy=placement.get("imagePullPolicy", "IfNotPresent"),
            command=["/opt/hermes/.venv/bin/hermes"],
            args=runtime.get("command")
            or ["serve", "--host", "127.0.0.1", "--port", str(self.settings.gateway_port)],
            env=[
                *environment,
                client.V1EnvVar(
                    name="HERMES_DASHBOARD_SESSION_TOKEN", value_from=token_env.value_from
                ),
            ],
            ports=[
                client.V1ContainerPort(name="gateway", container_port=self.settings.gateway_port)
            ],
            resources=client.V1ResourceRequirements(
                requests=resource_requests,
                limits=resource_limits,
            ),
            security_context=client.V1SecurityContext(
                allow_privilege_escalation=False,
                capabilities=client.V1Capabilities(drop=["ALL"]),
                run_as_non_root=True,
                run_as_user=10000,
                run_as_group=10000,
            ),
            volume_mounts=volume_mounts,
        )
        bridge = client.V1Container(
            name="runtime-bridge",
            image=self.settings.runtime_bridge_image,
            env=[
                client.V1EnvVar(
                    name="HERMES_GATEWAY_URL",
                    value=f"ws://127.0.0.1:{self.settings.gateway_port}/api/ws",
                ),
                token_env,
                client.V1EnvVar(name="EDITH_BRIDGE_TOKEN", value_from=token_env.value_from),
            ],
            ports=[client.V1ContainerPort(name="bridge", container_port=self.settings.bridge_port)],
            readiness_probe=client.V1Probe(
                http_get=client.V1HTTPGetAction(path="/health", port="bridge"),
                period_seconds=5,
                failure_threshold=12,
            ),
            security_context=client.V1SecurityContext(
                allow_privilege_escalation=False,
                capabilities=client.V1Capabilities(drop=["ALL"]),
                run_as_non_root=True,
                run_as_user=10001,
                run_as_group=10001,
            ),
        )
        pod_labels = {**selector, **{_name(key): _name(value) for key, value in labels.items()}}
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=workload, labels=selector),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels=selector),
                strategy=client.V1DeploymentStrategy(type="Recreate"),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels=pod_labels),
                    spec=client.V1PodSpec(
                        service_account_name=placement.get("serviceAccountName")
                        or self.settings.runtime_service_account,
                        automount_service_account_token=False,
                        security_context=client.V1PodSecurityContext(
                            run_as_non_root=True,
                            fs_group=10000,
                            seccomp_profile=client.V1SeccompProfile(type="RuntimeDefault"),
                        ),
                        containers=[hermes, bridge],
                        volumes=volumes,
                        image_pull_secrets=[
                            client.V1LocalObjectReference(name=name)
                            for name in (
                                placement.get("imagePullSecrets")
                                or self.settings.image_pull_secrets
                            )
                        ],
                        node_selector=placement.get("nodeSelector"),
                        tolerations=placement.get("tolerations"),
                        affinity=placement.get("affinity"),
                    ),
                ),
            ),
        )
        await self._apply(
            apps.create_namespaced_deployment,
            apps.patch_namespaced_deployment,
            workload,
            namespace,
            deployment,
        )
        service_body = client.V1Service(
            metadata=client.V1ObjectMeta(name=service, labels=selector),
            spec=client.V1ServiceSpec(
                selector=selector,
                ports=[
                    client.V1ServicePort(
                        name="bridge", port=self.settings.bridge_port, target_port="bridge"
                    )
                ],
                type="ClusterIP",
            ),
        )
        await self._apply(
            core.create_namespaced_service,
            core.patch_namespaced_service,
            service,
            namespace,
            service_body,
        )
        await self.wait_ready(namespace, workload)
        pods = await core.list_namespaced_pod(
            namespace, label_selector=",".join(f"{key}={value}" for key, value in selector.items())
        )
        pod = pods.items[0] if pods.items else None
        dns = f"{service}.{namespace}.svc"
        identity = {
            "provider": "kubernetes",
            "namespace": namespace,
            "workloadKind": "Deployment",
            "workloadName": workload,
            "podName": pod.metadata.name if pod else None,
            "podUid": pod.metadata.uid if pod else None,
            "serviceDnsName": dns,
            "image": image,
            "imageDigest": image.rsplit("@", 1)[1] if "@" in image else None,
        }
        connection = {
            "instanceId": instance_id,
            "transports": [
                {"kind": "http", "url": f"http://{dns}:{self.settings.bridge_port}"},
                {"kind": "sse", "url": f"http://{dns}:{self.settings.bridge_port}/events"},
            ],
            "authorization": {"scheme": "bearer", "token": gateway_token},
            "expiresAt": "9999-12-31T23:59:59Z",
        }
        return RuntimeArtifact(identity=identity, connection=connection)

    async def wait_ready(self, namespace: str, name: str, timeout: float = 600) -> None:
        apps, _ = self._apis()
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            deployment = await apps.read_namespaced_deployment_status(name, namespace)
            if deployment.status.available_replicas and deployment.status.available_replicas >= 1:
                return
            await asyncio.sleep(2)
        raise TimeoutError(f"Deployment {namespace}/{name} did not become ready")

    async def scale(self, identity: dict[str, Any], replicas: int) -> None:
        apps, _ = self._apis()
        await apps.patch_namespaced_deployment_scale(
            identity["workloadName"],
            identity["namespace"],
            {"spec": {"replicas": replicas}},
        )
        if replicas:
            await self.wait_ready(identity["namespace"], identity["workloadName"])

    async def delete(self, identity: dict[str, Any], retain_data: bool = False) -> None:
        apps, core = self._apis()
        namespace = identity["namespace"]
        name = identity["workloadName"]
        for call in (
            lambda: apps.delete_namespaced_deployment(name, namespace),
            lambda: core.delete_namespaced_service(name, namespace),
            lambda: core.delete_namespaced_secret(f"{name}-auth", namespace),
        ):
            try:
                await call()  # type: ignore[no-untyped-call]
            except ApiException as exc:
                if exc.status != 404:
                    raise
        if not retain_data:
            try:
                await core.delete_namespaced_persistent_volume_claim(f"{name}-data", namespace)
            except ApiException as exc:
                if exc.status != 404:
                    raise
