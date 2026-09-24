local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

//local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='router',
  createFrom=rescile.createFromProperty('network', asName='network'),
  resourceType='network',
  relationType='DEPENDS_ON',
  name= '{{- parent -}}-{{- value | lower -}}-' + aws.decode.network,
  properties={
    type: '{{- type -}}',
    cidr: '{{- segments[property.index] -}}',
    created: '{{- timestamp -}}',
  },
) + {
  segments: '{%- set count = origin_resource[0].network | length -%}{%- set range = origin_resource[0].cidr -%}{{- range | lib(path="network.rhai", function="cidr_split_n", n=count) | __rescile_safe_print -}}',
  parent: '{{- origin_resource[0].name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}',
  type: '{{- origin_resource[0].type | lower -}}',
  timestamp: '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}',
}
