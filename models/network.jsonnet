local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}';
local type = '{{- origin_resource.type | lower -}}';
local segments = '{{ origin_resource.cidr | lib(path="network.rhai", function="cidr_split_n", n=4) }}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='router',
  createFrom=rescile.createFromProperty('network', asName='network'),
  resourceType='network',
  relationType='DEPENDS_ON',
  name=parent + '-{{- value | lower -}}-' + aws.decode.network,
  properties={
    type: type,
    cidr: segments[1],
    created: timestamp,
  },
)
