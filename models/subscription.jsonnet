local rescile = import 'rescile/v1/rescile.libsonnet';
local provider = 'aws';

rescile.createResource(
  origin='resident',
  resourceType='subscription',
  relationType='OWNED_BY',
  name=std.asciiUpper(provider) + '-' + '{{- tenant -}}' + '-' + '{{- solution -}}',
  properties={
    provider: provider,
    type: '{{- solution -}}',
    home: 'Zurich',
    account: ['DEV', 'PROD', 'INT', 'EDU', 'TST'],
    util: ['vault', 'syslog'],
    logging: true,
    auditing: true,
    description: 'The subscription defines a cloud environment at ' + provider + ' that allows ' + '{{ tenant }}' + ' to deploy the ' + '{{ solution }}' + ' solution.',
    created: '{{- timestamp -}}',
  },
) + {
  tenant: '{{ params.tenant | upper }}',
  solution: '{{ params.solution | upper }}',
  timestamp: '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}',
}
