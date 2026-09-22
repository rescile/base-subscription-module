local rescile = import 'rescile/v1/rescile.libsonnet';
local aws = import 'aws.libsonnet';
local net = import 'network.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='router',
  createFrom=rescile.createFromProperty('network', asName='network'),
  resourceType='network',
  relationType='DEPENDS_ON',
  name=parent + '-{{ value | lower }}-' + aws.decode.network,
  properties={
    type: type,
    cidr: net.cidr_split_n('10.0.0.0/16', 4),
    created: timestamp,
  },
)
