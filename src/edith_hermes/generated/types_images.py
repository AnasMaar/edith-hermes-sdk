"""Generated wire-shape types; required keys are explicit. Do not edit."""
from __future__ import annotations
import builtins
from typing import Any, Literal, Union
from typing_extensions import Required, TypedDict, TypeAlias
from . import types_control_plane
from . import types_runtime
from . import types_tools
from . import types_inference
from . import types_native

OwnerReference = TypedDict('OwnerReference', {
    'tenantId': Required['str'],
    'subjectId': Required['str'],
}, total=False)

PackageSpec = TypedDict('PackageSpec', {
    'apt': 'builtins.list[str]',
    'python': 'builtins.list[str]',
    'node': 'builtins.list[str]',
}, total=False)

ArtifactMount = TypedDict('ArtifactMount', {
    'artifactId': Required['str'],
    'destination': Required['str'],
    'checksum': 'str',
    'mode': 'str',
}, total=False)

CreateImageRecipeRequest = TypedDict('CreateImageRecipeRequest', {
    'owner': Required['OwnerReference'],
    'name': Required['str'],
    'baseImage': Required['str'],
    'platforms': "builtins.list[Literal['linux/amd64', 'linux/arm64']]",
    'packages': 'PackageSpec',
    'artifacts': 'builtins.list[ArtifactMount]',
    'labels': 'dict[str, str]',
    'buildArguments': 'dict[str, str]',
    'runtime': 'CreateImageRecipeRequestRuntime',
}, total=False)

CreateImageRecipeRequestRuntime = TypedDict('CreateImageRecipeRequestRuntime', {
    'user': 'str',
    'command': 'builtins.list[str]',
    'exposedPorts': 'builtins.list[int]',
}, total=False)

ImageRecipe = TypedDict('ImageRecipe', {
    'owner': Required['OwnerReference'],
    'name': Required['str'],
    'baseImage': Required['str'],
    'platforms': "builtins.list[Literal['linux/amd64', 'linux/arm64']]",
    'packages': 'PackageSpec',
    'artifacts': 'builtins.list[ArtifactMount]',
    'labels': 'dict[str, str]',
    'buildArguments': 'dict[str, str]',
    'runtime': 'ImageRecipeRuntime',
    'id': Required['str'],
    'recipeDigest': Required['str'],
    'createdAt': Required['str'],
}, total=False)

ImageRecipeRuntime = TypedDict('ImageRecipeRuntime', {
    'user': 'str',
    'command': 'builtins.list[str]',
    'exposedPorts': 'builtins.list[int]',
}, total=False)

ImageRecipePage = TypedDict('ImageRecipePage', {
    'items': Required['builtins.list[ImageRecipe]'],
    'nextCursor': 'Union[str, None]',
}, total=False)

StartImageBuildRequest = TypedDict('StartImageBuildRequest', {
    'owner': Required['OwnerReference'],
    'source': Required['Union[StartImageBuildRequestSource0, StartImageBuildRequestSource1]'],
    'destination': Required['StartImageBuildRequestDestination'],
    'buildSecretRefs': 'builtins.list[str]',
    'cachePolicy': "Literal['use', 'refresh', 'disabled']",
    'verificationPolicy': "Literal['required', 'warn', 'disabled']",
}, total=False)

StartImageBuildRequestSource0 = TypedDict('StartImageBuildRequestSource0', {
    'recipeId': Required['str'],
}, total=False)

StartImageBuildRequestSource1 = TypedDict('StartImageBuildRequestSource1', {
    'recipe': Required['CreateImageRecipeRequest'],
}, total=False)

StartImageBuildRequestDestination = TypedDict('StartImageBuildRequestDestination', {
    'repository': Required['str'],
    'tags': 'builtins.list[str]',
    'registryCredentialRef': 'str',
}, total=False)

ImageBuild = TypedDict('ImageBuild', {
    'id': Required['str'],
    'owner': Required['OwnerReference'],
    'status': Required['BuildStatus'],
    'recipeDigest': 'str',
    'imageId': 'str',
    'progress': 'int',
    'error': 'Union[Problem, None]',
    'createdAt': Required['str'],
    'completedAt': 'Union[str, None]',
}, total=False)

ImageBuildPage = TypedDict('ImageBuildPage', {
    'items': Required['builtins.list[ImageBuild]'],
    'nextCursor': 'Union[str, None]',
}, total=False)

VerificationResult = TypedDict('VerificationResult', {
    'status': Required["Literal['pending', 'passed', 'warned', 'failed']"],
    'scanner': 'str',
    'criticalVulnerabilities': 'int',
    'highVulnerabilities': 'int',
    'policyViolations': 'builtins.list[str]',
}, total=False)

ManagedImage = TypedDict('ManagedImage', {
    'id': Required['str'],
    'owner': Required['OwnerReference'],
    'repository': Required['str'],
    'digest': Required['str'],
    'immutableReference': 'str',
    'platforms': Required['builtins.list[str]'],
    'recipeDigest': 'str',
    'sbomUrl': 'str',
    'provenanceUrl': 'str',
    'signatureBundleUrl': 'str',
    'verification': Required['VerificationResult'],
    'activeInstanceReferences': 'int',
    'createdAt': Required['str'],
}, total=False)

ManagedImagePage = TypedDict('ManagedImagePage', {
    'items': Required['builtins.list[ManagedImage]'],
    'nextCursor': 'Union[str, None]',
}, total=False)

Problem = TypedDict('Problem', {
    'type': Required['str'],
    'title': Required['str'],
    'status': Required['int'],
    'detail': 'str',
    'traceId': 'str',
}, total=False)

createImageRecipeRuntime = TypedDict('createImageRecipeRuntime', {
    'user': 'str',
    'command': 'builtins.list[str]',
    'exposedPorts': 'builtins.list[int]',
}, total=False)

startImageBuildSource0 = TypedDict('startImageBuildSource0', {
    'recipeId': Required['str'],
}, total=False)

startImageBuildSource1 = TypedDict('startImageBuildSource1', {
    'recipe': Required['CreateImageRecipeRequest'],
}, total=False)

startImageBuildDestination = TypedDict('startImageBuildDestination', {
    'repository': Required['str'],
    'tags': 'builtins.list[str]',
    'registryCredentialRef': 'str',
}, total=False)

BuildStatus: TypeAlias = Literal['queued', 'resolving', 'building', 'scanning', 'signing', 'publishing', 'succeeded', 'failed', 'cancelled']
