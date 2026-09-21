local locations = import 'location_codes.json';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | upper -}}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';
//local locs = [{%- for reg in origin_resource.regions | split(pat=',') %}'{{ reg | trim }}'{% if not loop.last %}, {% endif %}{%- endfor %}];


rescile.createResource(
  origin='account',
  createFrom=rescile.createFromProperty('regions', asName='region'),
  resourceType='region',
  relationType='DEFINED_BY',
  name=parent + '-{{ value | trim }}',
  properties={
    type: type,
    locs: locations['-{{ value | trim }}'].iata,  // This doesn`t work
    created: timestamp,
  },
)
