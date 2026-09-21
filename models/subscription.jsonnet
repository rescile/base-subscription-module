local rescile = import 'rescile/v1/rescile.libsonnet';

local provider = 'aws';
local tenant = '{{ params.tenant | upper }}';
local solution = '{{ params.solution | upper }}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='resident',
  resourceType='subscription',
  relationType='OWNED_BY',
  name=std.asciiUpper(provider) + '-' + tenant + '-' + solution,
  properties={
    operator: provider,
    type: solution,
    home: 'Zurich',
    account: ['DEV', 'PROD', 'INT'],
    util: ['vault', 'syslog'],
    logging: true,
    auditing: true,
    description: 'The subscription defines a cloud environment at ' + provider + ' that allows ' + tenant + ' to deploy the ' + solution + ' solution.',
    created: timestamp,
  },
  //id=provider
)
