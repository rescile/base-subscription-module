local rescile = import 'rescile/v1/rescile.libsonnet';

local provider = 'aws';
local tenant = 'corp';
local solution = 'finance';

rescile.createResource(
  origin='resident',
  resourceType='subscription',
  relationType='OWNED_BY',
  name=provider + '-test-management_account',
  //name='{{- provider_name | upper -}}-{{- params.solution | upper -}}-{{- provider.dictionary.subscription | upper -}}',
  properties={
    operator: provider,
    //type: '{{ params.solution }}',
    type: solution,
    home: 'Zurich',
    account: ['DEV', 'PROD', 'INT'],
    util: ['vault', 'syslog'],
    logging: true,
    auditing: true,
    description: 'The subscription defines a cloud environment at ' + provider + ', and allows {{ origin_resource.name | capitalize }} to manage it.',
    created: '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}',
  },
  id=provider
)
