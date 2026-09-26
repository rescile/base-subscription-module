local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

[
  rescile.createResource(
    origin='network',
    resourceType='gateway',
    relationType='DEFINED_BY',
    name=parent + '-' + aws.decode.gateway,
    properties={
      class: class,
      description: 'The ' + class + ' gateway is a network node that connects two different networks with dissimilar architectures and protocols so that data can flow between them.',
      created: timestamp,
    },
  ),
  rescile.createResource(
    origin='network',
    createFrom=rescile.createFromProperty('gateway', asName='gateway'),
    resourceType='gateway',
    relationType='DERIVED_FROM',
    name=parent + '-{{ value }}_' + aws.decode.gateway,
    properties={
      class: class,
      description: 'The {{ value | lower }} gateway is a network node that connects two different networks with dissimilar architectures and protocols so that data can flow between them.',
      created: timestamp,
    },
  )
]
