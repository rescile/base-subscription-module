local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | upper -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='account',
  createFrom=rescile.createFromProperty('regions', asName='region'),
  resourceType='region',
  relationType='DEFINED_BY',
  name=parent +'-{{ locations[value | trim].city | upper | default(value="") }}',
  properties={
    class: class,
    city: '{{ value | trim }}',
    country: '{{ locations[value | trim].country | default(value="") }}',
    timezone: '{{ locations[value | trim].tz | default(value="") }}',
    iata: '{{ locations[value | trim].iata | default(value="") }}',
    description: 'The {{ value }} cloud region is a distinct, isolated geographic area containing multiple physically separated and network-connected Availability Zones designed to provide high availability, fault tolerance, and low-latency infrastructure for cloud workloads.',
    created: timestamp,
  },
) + {
  locations: import 'location_codes.json',
}
