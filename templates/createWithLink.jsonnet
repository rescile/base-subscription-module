// This template describes how to create a new resources that is realted to an existing resource.
// An additional relation to existing resources is defined using the rescile.linkResource function.

local <provider> = import '<provider>.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

[
  rescile.createResource(
    origin='<parent_type>',
    resourceType='<resource_type>',
    relationType='DEFINED_BY',
    name=parent + '-<resource_type>',
    properties={
      class: class,
      description: '<description>',
      created: timestamp,
    },
  ),

  rescile.linkResources(
    origin='<resource_type>',
    withResource='<related_type>',
    joinLocal='<joined_property>',
    joinRemote='<joined_property>',
    relationType='DEPENDS_ON',
    copyProperties=[
      { from: '<source_property>', as: '<target_property>' },
    ],
  )
]
