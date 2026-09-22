local rescile = import 'rescile/v1/rescile.libsonnet';
local aws = import 'aws.libsonnet';

local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | lower -}}';
local parent = '{{- origin_resource.name -}}';
local solution = '{{ params.solution | lower }}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';
local location = '{{- origin_resource.city | lower -}}';
local cidr = '10.0.0.0/19';
local bgp = '172.16.0.1/30';
local vpn = 'tbd';

rescile.createResource(
  origin='region',
  resourceType='router',
  relationType='SATISFIES',
  name=provider + '-' + solution + '-' + location + '-' + aws.decode.router,
  properties={
    type: type,
    cidr: cidr,
    bgp: bgp,
    vpn: vpn,
    description: 'The ' + provider + ' ' + type + ' virtual ' + aws.decode.router + ' analyzes incoming data packets, determines the best path for them to travel across interconnected networks, and forwards them toward their intended destination.',
    created: timestamp,
  },
)


