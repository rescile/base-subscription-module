local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='wallet',
  createFrom=rescile.createFromProperty('certificate', asName='certificate'),
  resourceType= 'certificate',
  relationType='DERIVED_FROM',
  name=parent + '-{{ value | lower }}-{{- _type | lower -}}',
  properties={
    class: class,
    description: 'The {{ value | lower }} certificate verifies the identity of communicating endpoints and uses public key cryptography to encrypt data in transit, ensuring network traffic cannot be intercepted, modified, or tampered with.',
    created: timestamp,
  },
)
