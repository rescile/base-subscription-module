local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local cidr = '10.0.0.0/19';
local bgp = '172.16.0.1/30';
local vpn = 'tbd';

local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | lower -}}';
local parent = '{{- origin_resource.name -}}';
local solution = '{{ params.solution | lower }}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';
local location = '{{- origin_resource.city | lower -}}';

[
  rescile.createResource(
    origin='region',
    resourceType='router',
    relationType='SATISFIES',
    name=provider + '-' + solution + '-' + location + '-' + aws.decode.router,
    properties={
      class: class,
      provider: provider,
      cidr: cidr,
      bgp: bgp,
      vpn: vpn,
      description: 'The ' + provider + ' ' + class + ' virtual ' + aws.decode.router + ' analyzes incoming data packets, determines the best path for them to travel across interconnected networks, and forwards them toward their intended destination.',
      created: timestamp,
    },
  ),

  rescile.linkResources(
    origin='router',
    withResource='subscription',
    joinLocal='provider',
    joinRemote='provider',
    relationType='DEPENDS_ON',
    copyProperties=[
      { from: 'account', as: 'network' },
    ],
  ),
]
