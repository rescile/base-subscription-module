local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='endpoint',
  resourceType='compute',
  relationType='DERIVED_FROM',
  name=parent + aws.decode.compute + '-instance',
  properties={
    class: class,
    description: 'Compute infrastructure provided by ' + provider + ' is an on-demand, scalable processing power—ranging from virtual machines to serverless containers—that is managed entirely through code. Access and inter-node communication rely on dynamic, short-lived IAM tokens and automated TLS certificates rather than static passwords.',
    created: timestamp,
  },
)
