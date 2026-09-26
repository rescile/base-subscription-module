// This template describes how to derive new child resources from a parent. The parent captures the desired instances
// in a property that serves a list for the rescile.createFromProperty function.   


local aws = import 'aws.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | capitalize -}}';
local class = '{{- origin_resource.class | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

rescile.createResource(
  origin='network',
  createFrom=rescile.createFromProperty('firewall', asName='firewall'),
  resourceType='firewall',
  relationType='DERIVED_FROM',
  name=parent + '-{{ value }}-' + aws.decode.firewall,
  properties={
    class: '{% if value == "internet" %}public{% else %}private{% endif %}',
    filter: ['{{- filters["unrestricted-tcp-egress"] -}}', '{{- filters["dns-udp-ingress"] -}}', '{{- filters["dns-tcp-ingress"] -}}'],
    description: 'The {{ value }} firewall controls incoming (inbound) and outgoing (outbound) network traffic at the instance level.',
    created: timestamp,
  },
) + {
  filters: import 'firewall-rules.json'
}
