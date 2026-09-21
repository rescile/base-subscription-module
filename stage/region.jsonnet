local location = import 'location.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local regions = ['Zurich', 'Paris', 'London'];
local locations = '{{- origin_resource.regions | json_encode -}}';
local locs = std.extVar('{{- origin_resource.regions -}}');
//local regions = std.extVar('regions');

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | upper -}}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

[
  rescile.createResource(
    origin='account',
    resourceType='region',
    relationType='DEFINED_BY',
    name=parent + '-' + reg,
    properties={
      type: type,
      location: reg,
      code: std.asciiUpper(location.get(reg, 'iata')),
      timezone: location.get(reg, 'tz'),
      country: std.asciiUpper(location.get(reg, 'country')),
      created: timestamp,
      locs: locations,
      locs2: locs,
    },
  )
  for reg in regions
]
