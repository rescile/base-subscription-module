// This template describes how to derive new child resources from a parent and incorporate a json source for additional properties.
// The parent captures the desired instances in a property that serves a list for the rescile.createFromProperty function.
// The source_file holds data that are retrieved for additional properties per instance.   


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
    <input>: '{{ <source>[value | trim].<input> | default(value="") }}',
    created: timestamp,
  },
) + {
  <source>: import '<source_file>.json',
}
