local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='login',
  createFrom=rescile.createFromProperty('channel', asName='channel'),
  resourceType='channel',
  relationType='DERIVED_FROM',
  name=provider + '-{{- value | lower -}}-{{- _type | lower -}}',
  properties={
    class: class,
    description: 'The {{ value | lower }} channel enables communication for operators.',
    created: timestamp,
  },
)
