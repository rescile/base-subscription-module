local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | upper -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';
local home = '{{- origin_resource.home | capitalize -}}';

rescile.createResource(
  origin='subscription',
  resourceType='account',
  relationType='BASELINE_TEMPLATE',
  name=parent + '-ACCOUNT',
  properties={
    type: '{{- origin_resource.type | lower -}}',
    //environment = "{{- property.value | lower -}}"
    //template = "Core" # Only AWS
    region: [home, 'London', 'Paris'],
    description: 'The ' + provider + ' account an independently manageable IAM security boundary within the {{ origin_resource.name | capitalize }} subscription that enables a centralized management and grants authorized access to resources, services and configurations.',
    created: timestamp,
  },
  id=provider
)


//origin_resource = "subscription"

//provider_name = { "function!" = "{{- origin_resource.name | regexp(expr='s/^([^-]+)-.*/\\1/') | lower -}}" }
//decoder = { "json!" = "{{- provider_name -}}-decoder.json" }

//[[create_resource]]
//create_from = { property = "account" }
//relation_type = "BASELINE_TEMPLATE"
//name = "{{- origin_resource.name | regexp(expr='s/^([^-]+-[^-]+)-.*/\\1/') | upper -}}-{{- property.value  | upper -}}-{{- decoder.resource.account | upper -}}"
//[create_resource.properties]
//function = "{{- origin_resource.function | lower -}}"
//provider = "{{- provider_name -}}"
//environment = "{{- property.value | lower -}}"
//template = "Core" # Only AWS
//region = ["{{- origin_resource.home -}}", "London", "Paris"] # for multi region deployments
//description = "The {{ provider_name | upper }} account an independently manageable IAM security boundary within the {{ origin_resource.name | capitalize }} subscription that enables a centralized management and grants authorized access to resources, services and configurations."
//created = "{{- now(utc=true) | date(format='%Y-%m-%dT%H:%M:%SZ') -}}"
