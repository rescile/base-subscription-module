local rescile = import 'rescile/v1/rescile.libsonnet';

local tenant = '{{ params.tenant | capitalize }}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  resourceType='resident',
  name=tenant,
  relationType='BASELINE_TEMPLATE',
  properties={
    description: 'The resident represents ' + tenant + ' and isolates data and applications from other cloud users through dedicated partitions of compute, storage and network resources.',
    created: timestamp,
  },
)
