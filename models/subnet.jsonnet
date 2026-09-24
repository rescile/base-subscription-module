local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='network',
  createFrom=rescile.createFromProperty('subnet', asName='subnet'),
  resourceType='subnet',
  relationType='DERIVED_FROM',
  name= parent + '-{{- value | lower -}}',
  properties={
    class: class,
    cidr: '{%- set count = origin_resource.subnet | length -%}' +
          '{%- set split_cidrs = origin_resource.cidr | lib(path="network.rhai", function="cidr_split_n", n=count) -%}' +
          '{{ split_cidrs[property.index] }}',
    created: timestamp,
  },
)
