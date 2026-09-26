local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local firewall = ["default","internet"];
local subnet = ["a", "b"];
local gateway = ["default"];

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='router',
  createFrom=rescile.createFromProperty('network', asName='network'),
  resourceType='network',
  relationType='DEPENDS_ON',
  name=parent + '-{{- value | lower -}}-' + aws.decode.network,
  properties={
    class: class,
    cidr: '{{- segments[property.index] -}}',
    firewall: firewall,
    subnet: subnet,
    gateway: gateway,
    description: "The ' + class +  ' network is an virtual, on-demand infrastructure that connects users and applications to computing resources like servers, storage, and software, all delivered over the internet.",
    created: timestamp,
  },
) + {
  segments: '{%- set count = origin_resource[0].network | length -%}{%- set range = origin_resource[0].cidr -%}{{- range | lib(path="network.rhai", function="cidr_split_n", n=count) | __rescile_safe_print -}}',
}
