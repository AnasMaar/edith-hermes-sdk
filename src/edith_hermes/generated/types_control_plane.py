"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_images
from . import types_runtime
from . import types_tools
from . import types_inference
from . import types_native

ControlPlaneCapabilities = TypedDict('ControlPlaneCapabilities', {
    'runtimeProviders': Required['builtins.list[RuntimeKind]'],
    'stateBackend': Required["Literal['memory', 'sqlite', 'postgresql', 'sql']"],
    'authentication': Required["Literal['none', 'static', 'oidc']"],
    'imageSecurity': Required['ControlPlaneCapabilitiesImageSecurity'],
    'durableJobs': 'bool',
    'multiReplicaSafe': 'bool',
}, total=False)

ControlPlaneCapabilitiesImageSecurity = TypedDict('ControlPlaneCapabilitiesImageSecurity', {
    'digestPinnedBase': Required['bool'],
    'vulnerabilityScan': Required['bool'],
    'signature': Required['bool'],
}, total=False)

Problem = TypedDict('Problem', {
    'type': Required['str'],
    'title': Required['str'],
    'status': Required['int'],
    'detail': 'str',
    'instance': 'str',
    'code': 'str',
    'retryable': 'bool',
}, total=False)

ResourceRequirements = TypedDict('ResourceRequirements', {
    'cpu': 'ResourceQuantity',
    'memory': 'ResourceQuantity',
    'gpu': 'int',
    'ephemeralStorage': 'ResourceQuantity',
}, total=False)

SecretReference = TypedDict('SecretReference', {
    'name': Required['str'],
    'key': 'str',
    'version': 'str',
}, total=False)

EnvironmentValue0 = TypedDict('EnvironmentValue0', {
    'value': Required['str'],
}, total=False)

EnvironmentValue1 = TypedDict('EnvironmentValue1', {
    'secretRef': Required['SecretReference'],
}, total=False)

VolumeMount = TypedDict('VolumeMount', {
    'name': Required['str'],
    'mountPath': Required['str'],
    'readOnly': 'bool',
    'source': 'VolumeMountSource',
}, total=False)

VolumeMountSource = TypedDict('VolumeMountSource', {
    'persistentVolumeClaim': 'str',
    'hostPath': 'str',
    'emptyDir': 'bool',
}, total=False)

KubernetesPlacement = TypedDict('KubernetesPlacement', {
    'context': 'str',
    'namespace': 'str',
    'serviceAccountName': 'str',
    'nodeSelector': 'dict[str, str]',
    'tolerations': 'builtins.list[dict[str, Any]]',
    'affinity': 'dict[str, Any]',
    'podTemplateMetadata': 'dict[str, Any]',
    'imagePullPolicy': "Literal['Always', 'IfNotPresent', 'Never']",
    'imagePullSecrets': 'builtins.list[str]',
    'storageClassName': 'str',
    'persistentVolumeSize': 'ResourceQuantity',
}, total=False)

RuntimeSpec = TypedDict('RuntimeSpec', {
    'kind': Required['RuntimeKind'],
    'image': 'str',
    'managedImageId': 'str',
    'imageDigest': 'str',
    'executable': 'str',
    'command': 'builtins.list[str]',
    'hermesHome': 'str',
    'endpoint': 'str',
    'authorization': 'RuntimeSpecAuthorization',
    'resources': 'ResourceRequirements',
    'environment': 'dict[str, EnvironmentValue]',
    'volumes': 'builtins.list[VolumeMount]',
    'skipReadinessCheck': 'bool',
    'extraHosts': 'dict[str, str]',
    'kubernetes': 'KubernetesPlacement',
    'cloud': 'dict[str, Any]',
}, total=False)

RuntimeSpecAuthorization = TypedDict('RuntimeSpecAuthorization', {
    'scheme': "Literal['bearer', 'websocket_ticket', 'dashboard_password', 'none']",
    'username': 'str',
    'password': 'str',
    'token': 'str',
}, total=False)

BootstrapSpec = TypedDict('BootstrapSpec', {
    'profile': 'CreateProfileRequest',
    'mcpServers': 'builtins.list[str]',
    'toolBundles': 'builtins.list[str]',
    'config': 'dict[str, Any]',
}, total=False)

CreateInstanceRequest = TypedDict('CreateInstanceRequest', {
    'owner': Required['OwnerReference'],
    'name': Required['str'],
    'runtime': Required['RuntimeSpec'],
    'poolId': 'str',
    'labels': 'dict[str, str]',
    'bootstrap': 'BootstrapSpec',
}, total=False)

UpdateInstanceRequest = TypedDict('UpdateInstanceRequest', {
    'name': 'str',
    'desiredState': 'DesiredState',
    'labels': 'dict[str, str]',
    'runtime': 'RuntimeSpec',
}, total=False)

Instance = TypedDict('Instance', {
    'id': Required['str'],
    'owner': Required['OwnerReference'],
    'name': Required['str'],
    'runtime': Required['RuntimeSpec'],
    'status': Required['InstanceStatus'],
    'desiredState': Required['DesiredState'],
    'poolId': 'Union[str, None]',
    'labels': 'dict[str, str]',
    'health': 'InstanceHealth',
    'runtimeIdentity': 'RuntimeIdentity',
    'revision': Required['str'],
    'createdAt': Required['str'],
    'updatedAt': Required['str'],
}, total=False)

InstanceHealth = TypedDict('InstanceHealth', {
    'ready': 'bool',
    'reason': 'str',
    'checkedAt': 'str',
}, total=False)

RuntimeIdentity = TypedDict('RuntimeIdentity', {
    'provider': "Literal['external', 'process', 'container', 'kubernetes', 'nous_cloud']",
    'endpoint': 'str',
    'processId': 'int',
    'containerId': 'str',
    'containerName': 'str',
    'cluster': 'str',
    'namespace': 'str',
    'workloadKind': "Literal['StatefulSet', 'Deployment', 'Pod', 'Job']",
    'workloadName': 'str',
    'podName': 'str',
    'podUid': 'str',
    'ordinal': 'int',
    'serviceDnsName': 'str',
    'image': 'str',
    'imageDigest': 'str',
}, total=False)

OwnerReference = TypedDict('OwnerReference', {
    'tenantId': Required['str'],
    'subjectId': Required['str'],
}, total=False)

InstancePage = TypedDict('InstancePage', {
    'items': Required['builtins.list[Instance]'],
    'nextCursor': 'Union[str, None]',
}, total=False)

InstanceOperation = TypedDict('InstanceOperation', {
    'id': Required['str'],
    'instanceId': Required['str'],
    'action': Required['str'],
    'status': Required['OperationStatus'],
    'error': 'Union[Problem, None]',
    'createdAt': Required['str'],
    'completedAt': 'Union[str, None]',
}, total=False)

ConnectionDescriptor = TypedDict('ConnectionDescriptor', {
    'instanceId': Required['str'],
    'transports': Required['builtins.list[ConnectionDescriptorTransportsItem]'],
    'authorization': 'ConnectionDescriptorAuthorization',
    'expiresAt': Required['str'],
}, total=False)

ConnectionDescriptorTransportsItem = TypedDict('ConnectionDescriptorTransportsItem', {
    'kind': Required["Literal['websocket', 'stdio', 'http', 'sse']"],
    'url': 'str',
    'command': 'builtins.list[str]',
    'protocols': 'builtins.list[str]',
}, total=False)

ConnectionDescriptorAuthorization = TypedDict('ConnectionDescriptorAuthorization', {
    'scheme': "Literal['bearer', 'websocket_ticket', 'dashboard_password', 'process_stdio', 'none']",
    'username': 'str',
    'password': 'str',
    'token': 'str',
}, total=False)

CapabilityDocument = TypedDict('CapabilityDocument', {
    'instanceId': Required['str'],
    'hermesVersion': 'str',
    'contracts': Required['builtins.list[CapabilityDocumentContractsItem]'],
    'domains': Required['dict[str, bool]'],
    'nativeMethods': 'builtins.list[str]',
}, total=False)

CapabilityDocumentContractsItem = TypedDict('CapabilityDocumentContractsItem', {
    'kind': Required["Literal['openrpc', 'openapi', 'mcp', 'acp']"],
    'version': Required['str'],
    'url': 'str',
    'revision': 'str',
}, total=False)

CreateProfileRequest = TypedDict('CreateProfileRequest', {
    'name': Required['str'],
    'description': 'str',
    'cloneFrom': 'str',
    'cloneAll': 'bool',
    'cloneChannels': 'bool',
    'includeSkills': 'bool',
    'soul': 'str',
    'model': 'str',
    'provider': 'str',
    'mirrorCredentials': 'bool',
    'config': 'dict[str, Any]',
}, total=False)

UpdateProfileRequest = TypedDict('UpdateProfileRequest', {
    'description': 'str',
    'soul': 'str',
    'model': 'str',
    'provider': 'str',
    'config': 'dict[str, Any]',
}, total=False)

Profile = TypedDict('Profile', {
    'id': Required['str'],
    'instanceId': Required['str'],
    'name': Required['str'],
    'description': 'str',
    'path': Required['str'],
    'model': 'str',
    'provider': 'str',
    'status': "Literal['ready', 'degraded', 'disabled']",
    'createdAt': Required['str'],
}, total=False)

InstanceTemplate = TypedDict('InstanceTemplate', {
    'runtime': Required['RuntimeSpec'],
    'bootstrap': 'BootstrapSpec',
    'labels': 'dict[str, str]',
}, total=False)

CreatePoolRequest = TypedDict('CreatePoolRequest', {
    'name': Required['str'],
    'template': Required['InstanceTemplate'],
    'minimumSize': 'int',
    'maximumSize': 'int',
    'desiredSize': 'int',
    'strategy': 'SchedulingStrategy',
    'idleTtlSeconds': 'int',
    'kubernetes': 'KubernetesPoolSpec',
}, total=False)

KubernetesPoolSpec = TypedDict('KubernetesPoolSpec', {
    'workloadName': Required['str'],
    'namespace': Required['str'],
    'controller': "Literal['StatefulSet']",
    'headlessServiceName': 'str',
    'volumeClaimTemplateName': 'str',
    'replicaOwnership': "Literal['sdk_control_plane']",
}, total=False)

UpdatePoolRequest = TypedDict('UpdatePoolRequest', {
    'minimumSize': 'int',
    'maximumSize': 'int',
    'desiredSize': 'int',
    'strategy': 'SchedulingStrategy',
    'idleTtlSeconds': 'int',
}, total=False)

InstancePool = TypedDict('InstancePool', {
    'name': Required['str'],
    'template': Required['InstanceTemplate'],
    'minimumSize': 'int',
    'maximumSize': 'int',
    'desiredSize': 'int',
    'strategy': 'SchedulingStrategy',
    'idleTtlSeconds': 'int',
    'kubernetes': 'KubernetesPoolSpec',
    'id': Required['str'],
    'status': Required["Literal['reconciling', 'ready', 'degraded', 'failed']"],
    'currentSize': Required['int'],
    'readySize': Required['int'],
    'createdAt': Required['str'],
}, total=False)

AcquireLeaseRequest = TypedDict('AcquireLeaseRequest', {
    'stickyKey': 'str',
    'ttlSeconds': 'int',
    'requiredLabels': 'dict[str, str]',
    'profile': 'Union[AcquireLeaseRequestProfile0, CreateProfileRequest]',
}, total=False)

AcquireLeaseRequestProfile0 = TypedDict('AcquireLeaseRequestProfile0', {
    'profileId': Required['str'],
}, total=False)

InstanceLease = TypedDict('InstanceLease', {
    'id': Required['str'],
    'poolId': Required['str'],
    'instanceId': Required['str'],
    'profileId': 'str',
    'connection': Required['ConnectionDescriptor'],
    'expiresAt': Required['str'],
}, total=False)

ProvisionUserInstanceRequest = TypedDict('ProvisionUserInstanceRequest', {
    'owner': Required['OwnerReference'],
    'name': Required['str'],
    'image': 'Union[ProvisionUserInstanceRequestImage0, ProvisionUserInstanceRequestImage1]',
    'runtime': Required['ProvisionUserInstanceRequestRuntime'],
    'bootstrap': 'BootstrapSpec',
    'labels': 'dict[str, str]',
}, total=False)

ProvisionUserInstanceRequestImage0 = TypedDict('ProvisionUserInstanceRequestImage0', {
    'managedImageId': Required['str'],
}, total=False)

ProvisionUserInstanceRequestImage1 = TypedDict('ProvisionUserInstanceRequestImage1', {
    'build': Required['ProvisionUserInstanceRequestImage1Build'],
}, total=False)

ProvisionUserInstanceRequestImage1Build = TypedDict('ProvisionUserInstanceRequestImage1Build', {
    'recipe': Required['types_images.CreateImageRecipeRequest'],
    'repository': Required['str'],
    'registryCredentialRef': 'str',
    'reuseMatchingImage': 'bool',
}, total=False)

ProvisionUserInstanceRequestRuntime = TypedDict('ProvisionUserInstanceRequestRuntime', {
    'kind': Required["Literal['external', 'process', 'container', 'kubernetes', 'nous_cloud']"],
    'image': 'str',
    'executable': 'str',
    'command': 'builtins.list[str]',
    'hermesHome': 'str',
    'endpoint': 'str',
    'authorization': 'dict[str, Any]',
    'environment': 'dict[str, EnvironmentValue]',
    'volumes': 'builtins.list[VolumeMount]',
    'skipReadinessCheck': 'bool',
    'extraHosts': 'dict[str, str]',
    'poolId': 'str',
    'resources': 'ResourceRequirements',
    'kubernetes': 'KubernetesPlacement',
}, total=False)

ProvisioningJob = TypedDict('ProvisioningJob', {
    'id': Required['str'],
    'owner': Required['OwnerReference'],
    'phase': Required['ProvisioningPhase'],
    'imageBuildId': 'str',
    'managedImageId': 'str',
    'instanceId': 'str',
    'profileId': 'str',
    'connection': 'ConnectionDescriptor',
    'error': 'Union[Problem, None]',
    'createdAt': Required['str'],
    'completedAt': 'Union[str, None]',
}, total=False)

listProfilesResult = TypedDict('listProfilesResult', {
    'items': Required['builtins.list[Profile]'],
}, total=False)

listPoolsResult = TypedDict('listPoolsResult', {
    'items': Required['builtins.list[InstancePool]'],
}, total=False)

acquireInstanceLeaseProfile0 = TypedDict('acquireInstanceLeaseProfile0', {
    'profileId': Required['str'],
}, total=False)

provisionUserInstanceImage0 = TypedDict('provisionUserInstanceImage0', {
    'managedImageId': Required['str'],
}, total=False)

provisionUserInstanceImage1 = TypedDict('provisionUserInstanceImage1', {
    'build': Required['provisionUserInstanceImage1Build'],
}, total=False)

provisionUserInstanceImage1Build = TypedDict('provisionUserInstanceImage1Build', {
    'recipe': Required['types_images.CreateImageRecipeRequest'],
    'repository': Required['str'],
    'registryCredentialRef': 'str',
    'reuseMatchingImage': 'bool',
}, total=False)

provisionUserInstanceRuntime = TypedDict('provisionUserInstanceRuntime', {
    'kind': Required["Literal['external', 'process', 'container', 'kubernetes', 'nous_cloud']"],
    'image': 'str',
    'executable': 'str',
    'command': 'builtins.list[str]',
    'hermesHome': 'str',
    'endpoint': 'str',
    'authorization': 'dict[str, Any]',
    'environment': 'dict[str, EnvironmentValue]',
    'volumes': 'builtins.list[VolumeMount]',
    'skipReadinessCheck': 'bool',
    'extraHosts': 'dict[str, str]',
    'poolId': 'str',
    'resources': 'ResourceRequirements',
    'kubernetes': 'KubernetesPlacement',
}, total=False)

RuntimeKind: TypeAlias = Literal['external', 'process', 'container', 'kubernetes', 'nous_cloud']

InstanceStatus: TypeAlias = Literal['pending', 'provisioning', 'starting', 'ready', 'draining', 'stopped', 'degraded', 'failed', 'deleting']

DesiredState: TypeAlias = Literal['running', 'stopped', 'deleted']

ResourceQuantity: TypeAlias = Union[str, float]

EnvironmentValue: TypeAlias = Union[EnvironmentValue0, EnvironmentValue1]

OperationStatus: TypeAlias = Literal['queued', 'running', 'succeeded', 'failed', 'cancelled']

SchedulingStrategy: TypeAlias = Literal['round_robin', 'least_sessions', 'least_busy', 'random', 'sticky_key', 'custom']

ProvisioningPhase: TypeAlias = Literal['queued', 'resolving_image', 'building_image', 'verifying_image', 'creating_instance', 'waiting_for_runtime', 'bootstrapping_profile', 'ready', 'failed', 'cancelled']
