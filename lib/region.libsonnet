// region.libsonnet
local locations = import 'location_codes.json';
local rescile = import 'rescile/v1/rescile.libsonnet';

{
  // Function to build a single resource given a region code
  buildRegionResource(regionKey, parent, provider, type, timestamp)::
    // Look up reference data safely from location_codes.json
    local loc = std.get(locations, regionKey, default={ iata: 'UNKNOWN', tz: 'UTC', country: 'UNKNOWN' });

    rescile.createResource(
      origin='account',
      createFrom=rescile.createFromProperty('region', asName='region'),
      resourceType='region',
      relationType='DEFINED_BY',
      name=parent + '-' + regionKey,
      properties={
        type: type,
        location: std.asciiUpper(std.substr(regionKey, 0, 1)) + std.substr(regionKey, 1, std.length(regionKey) - 1),
        code: std.asciiUpper(loc.iata),
        timezone: loc.tz,
        country: std.asciiUpper(loc.country),
        description: 'The region ' + regionKey + ' refers to a ' + provider + ' data center where management applications are hosted and data is stored, protected by privacy laws of the resident.',
        created: timestamp,
      },
    ),

  // Function to process an array of region keys
  buildAllRegions(regionArray, parent, provider, type, timestamp)::
    [
      self.buildRegionResource(regionKey, parent, provider, type, timestamp)
      for regionKey in regionArray
    ],
}
