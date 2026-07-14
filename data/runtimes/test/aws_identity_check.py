#!/usr/bin/env python3
# AWS Identity Check Script
# This script verifies your AWS identity and organization context using Boto3
import json
import subprocess

import boto3
from botocore.exceptions import ClientError


def get_rescile_secret(secret_name):
    """Helper to query the local rescile-ce vault."""
    try:
        cmd = ["rescile-ce", "vault", "secret", "get", "aws", secret_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Rescile Vault Fetch Failed for {secret_name}: {e.stderr.strip()}")
        return None

def main():
    print("=" * 60)
    print("🔐 FETCHING CREDENTIALS FROM RESCILE VAULT")
    print("=" * 60)

    # 1. Dynamically retrieve keys from your specific vault path
    access_key = get_rescile_secret("AWS_ACCESS_KEY_ID")
    secret_key = get_rescile_secret("AWS_SECRET_ACCESS_KEY")

    # Check if a session token also exists in your vault configuration (common for SSO)
    session_token = get_rescile_secret("AWS_SESSION_TOKEN")

    if not access_key or not secret_key:
        print("\n❌ Extraction aborted: Missing core keys in Rescile.")
        return

    print("✅ Credentials successfully loaded into script runtime memory.")

    # 2. Spin up unmanaged boto3 clients targeting your default infrastructure hub
    region = "eu-central-2"
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token if session_token else None,
        region_name=region
    )

    sts_client = session.client("sts")
    org_client = session.client("organizations")

    print("\n" + "=" * 60)
    print("🚀 EXECUTING AWS RECONNAISSANCE SWEEP")
    print("=" * 60)

    # 3. Step 1: Active Caller ID Verification
    account_id = None
    try:
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f"📍 Active Account ID : {account_id}")
        print(f"📍 Target Region     : {region}")
        print(f"📍 Assumed Identity  : {identity['Arn']}")
    except ClientError as e:
        print(f"❌ STS Identity Lookup Failed: {e.response['Error']['Message']}")
        return

    # 4. Step 2: Global Organization Inspection
    try:
        org_desc = org_client.describe_organization()
        org_data = org_desc["Organization"]
        print(f"\n✅ Organization Context Found:")
        print(f"   - Org ID           : {org_data['Id']}")
        print(f"   - Management Acct  : {org_data['MasterAccountId']}")
        print(f"   - Features Enabled : {org_data['FeatureSet']}")
    except ClientError as e:
        print(f"\n⚠️  describe_organization blocked: {e.response['Error']['Message']}")

    # 5. Step 3: Local Upstream Parent Lookup
    try:
        parents_response = org_client.list_parents(ChildId=account_id)
        print(f"\n✅ Direct Upstream Parent Mapping for Account {account_id}:")
        for parent in parents_response["Parents"]:
            print(f"   - Parent Container ID : {parent['Id']} (Type: {parent['Type']})")
    except ClientError as e:
        print(f"\n⚠️  list_parents (for local account) blocked: {e.response['Error']['Message']}")

    # 6. Step 4: Tree Root Evaluation
    try:
        roots_response = org_client.list_roots()
        print(f"\n✅ Global Roots Visible:")
        for root in roots_response["Roots"]:
            print(f"   - Root Target ID      : {root['Id']} (Name: {root['Name']})")
    except ClientError as e:
        print(f"\n⚠️  list_roots completely blocked: {e.response['Error']['Message']}")

    print("\n" + "=" * 60)
    print("🏁 SWEEP COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
