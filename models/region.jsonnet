local aws = import 'aws.libsonnet';
local regionHelper = import 'region.libsonnet';
local rescile = import 'rescile/v1/rescile.libsonnet';

local parent = '{{- origin_resource.name | regexp(expr="s/^([^-]+-[^-]+-[^-]+)-.*/\\1/") | lower -}}';
local provider = '{{- origin_resource.name | regexp(expr="s/^([^-]+)-.*/\\1/") | upper -}}';
local type = '{{- origin_resource.type | lower -}}';
local timestamp = '{{- now(utc=true) | date(format="%Y-%m-%dT%H:%M:%SZ") -}}';

local targetRegions = ['Zurich', 'London', 'Paris'];

// Generate all resources
regionHelper.buildAllRegions(targetRegions, parent, provider, type, timestamp)
