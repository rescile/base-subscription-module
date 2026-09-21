local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | upper -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';
local home = '{{- origin_resource.home | capitalize -}}';

rescile.createResource(
  origin='subscription',
  createFrom=rescile.createFromProperty('account', asName='account'),
  resourceType='account',
  relationType='BASELINE_TEMPLATE',
  name=parent + '-{{ value }}',
  properties={
    type: type,
    environment: '{{- value | lower -}}',
    //template = "Core" # Only AWS
    regions: [home, 'London', 'Paris'],
    description: 'The ' + provider + ' ' + aws.decode.account + ' defines an independently manageable IAM security boundary for the {{ origin_resource.name | upper }} subscription that enables a centralized management and grants authorized access to resources, services and configurations.',
    created: timestamp,
  },
)
