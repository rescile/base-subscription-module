local rescile = import 'rescile/v1/rescile.libsonnet';

rescile.linkResources(
  origin='router',
  withResource='subscription',
  joinLocal='provider',
  joinRemote='provider',
  relationType='DEPENDS_ON',
  copyProperties=[
    { from: 'account', as: 'network' },
  ],
)
