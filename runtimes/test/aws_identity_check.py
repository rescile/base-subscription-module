#!/usr/bin/env python3

# AWS Identity Check Script - Enhanced with Color Coding

import json
import subprocess
import boto3
from botocore.exceptions import ClientError

# ANSI Color Codes
class COLORS:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, color=COLORS.BLUE):
    print(f"{color}{message}{COLORS.ENDC}")

def get_rescile_secret(secret_name):
    try:
        cmd = ["rescile-ce", "vault", "secret", "get", "aws", secret_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{COLORS.FAIL}❌ Rescile Vault Fetch Failed for {secret_name}: {e.stderr.strip()}{COLORS.ENDC}")
        return None

def main():
    print(f"\n{COLORS.HEADER}{'=' * 60}")
    print("FETCHING CREDENTIALS FROM RESCILE VAULT")
    print(f"{'=' * 60}{COLORS.ENDC}")

    access_key = get_rescile_secret("AWS_ACCESS_KEY_ID")
    secret_key = get_rescile_secret("AWS_SECRET_ACCESS_KEY")
    session_token = get_rescile_secret("AWS_SESSION_TOKEN")

    if not access_key or not secret_key:
        print(f"\n{COLORS.FAIL}❌ Extraction aborted: Missing core keys in Rescile.{COLORS.ENDC}")
        return

    print(f"{COLORS.GREEN}✔ Credentials successfully loaded into runtime memory.{COLORS.ENDC}")

    region = "eu-central-2"
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token if session_token else None,
        region_name=region
    )

    sts_client = session.client("sts")
    org_client = session.client("organizations")

    print(f"\n{COLORS.HEADER}{'=' * 60}")
    print("EXECUTING AWS RECONNAISSANCE SWEEP")
    print(f"{'=' * 60}{COLORS.ENDC}")

    # Identity Verification
    try:
        identity = sts_client.get_caller_identity()
        account_id = identity["Account"]
        print(f"{COLORS.BOLD}Active Account ID :{COLORS.ENDC} {account_id}")
        print(f"{COLORS.BOLD}Target Region     :{COLORS.ENDC} {region}")
        print(f"{COLORS.BOLD}Assumed Identity  :{COLORS.ENDC} {identity['Arn']}")
    except ClientError as e:
        print(f"{COLORS.FAIL}STS Identity Lookup Failed: {e.response['Error']['Message']}{COLORS.ENDC}")
        return

    # Organization Inspection
    try:
        org_data = org_client.describe_organization()["Organization"]
        print(f"\n{COLORS.BLUE}Organization Context:{COLORS.ENDC}")
        print(f"  - Org ID         : {org_data['Id']}")
        print(f"  - Management Acct: {org_data['MasterAccountId']}")
        print(f"  - Features       : {org_data['FeatureSet']}")
    except ClientError as e:
        print(f"\n{COLORS.WARNING}describe_organization blocked: {e.response['Error']['Message']}{COLORS.ENDC}")

    # Local Parent Lookup
    try:
        parents = org_client.list_parents(ChildId=account_id)["Parents"]
        print(f"\n{COLORS.BLUE}Direct Upstream Parent Mapping:{COLORS.ENDC}")
        for p in parents:
            print(f"  - Parent Container ID : {p['Id']} (Type: {p['Type']})")
    except ClientError as e:
        print(f"\n{COLORS.WARNING}list_parents blocked: {e.response['Error']['Message']}{COLORS.ENDC}")

    # Tree Root Evaluation
    try:
        roots = org_client.list_roots()["Roots"]
        print(f"\n{COLORS.BLUE}Global Roots Visible:{COLORS.ENDC}")
        for r in roots:
            print(f"  - Root Target ID      : {r['Id']} (Name: {r['Name']})")
    except ClientError as e:
        print(f"\n{COLORS.FAIL}list_roots blocked: {e.response['Error']['Message']}{COLORS.ENDC}")

    print(f"\n{COLORS.HEADER}{'=' * 60}")
    print(f"{COLORS.GREEN}🏁 SWEEP COMPLETE{COLORS.ENDC}")
    print(f"{COLORS.HEADER}{'=' * 60}{COLORS.ENDC}")

if __name__ == "__main__":
    main()
