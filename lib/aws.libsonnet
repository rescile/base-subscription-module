// aws.libsonnet
{
  title: 'AWS Provider Library',
  version: '1.0',
  provider: 'AWS',
  decode: {
    subscription: 'management_account',
    account: 'accountTest',
    network: 'vpc',
    subnet: 'subnet',
    router: 'transit_gateway',
    gateway: 'gateway',
    vault: 'kms',
    wallet: 'wallet',
    resolver: 'resolver',
    zone: 'hostedzone',
    record: 'record',
    region: 'region',
    kubernetes: 'eks',
    firewall: 'security_group',
  },
}
