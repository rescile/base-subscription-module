local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{ origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | lower }}';
local class = '{{ origin_resource.class | lower }}';
//local port_filter = '{{ origin_resouce.filter }}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='firewall',
  resourceType='resolver',
  relationType='DEFINED_BY',
  name=provider + '_' + class + '-dns-' + aws.decode.resolver,
  properties={
    class: class,
    description: 'The ' + provider + ' DNS resolver is a managed, authoritative name service that operates exclusively within the control plane of a cloud network.',
    ports: '{%- set p = [] -%}{%- set filters = origin_resource.filter -%}{% for f in filters %}{%- set_global p = p | concat(with=f.port) -%}{%- endfor -%}{{- p | unique | safe -}}',
    created: timestamp,
  },
  //match=[rescile.inList(port_filter,53)]
)
