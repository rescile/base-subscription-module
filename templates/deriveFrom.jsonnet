// This template describes how to derive new child resources from a parent. The parent captures the desired instances
// in a property that serves a list for the rescile.createFromProperty function.   


local <provider> = import '<provider>.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='<parent_type>',
  createFrom=rescile.createFromProperty('<resource_type>', asName='<resource_type>'),
  resourceType='<resource_type>',
  relationType='DERIVED_FROM',
  name=parent + '-{{ value }}',
  properties={
    class: class,
    description: '<description>',
    created: timestamp,
  },
)
