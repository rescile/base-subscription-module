local rescile = import 'rescile/v1/rescile.libsonnet';

rescile.createResource(
  origin='account',
  createFrom=rescile.createFromProperty('regions', asName='region'),
  resourceType='region',
  relationType='DEFINED_BY',
  name='{{- parent -}}-{{ locations[value | trim].city | upper | default(value="") }}',
  properties={
    class: '{{- class -}}',
    city: '{{ value | trim }}',
    country: '{{ locations[value | trim].country | default(value="") }}',
    timezone: '{{ locations[value | trim].tz | default(value="") }}',
    iata: '{{ locations[value | trim].iata | default(value="") }}',
    created: '{{- timestamp -}}',
  },
) + {
  locations: import 'location_codes.json',
  parent: '{{- origin_resource[0].name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | upper -}}',
  class: '{{- origin_resource[0].class | lower -}}',
  timestamp: '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}',
}
