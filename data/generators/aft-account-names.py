#!/usr/bin/env python3
"""
Retrieve all AWS accounts managed by Control Tower (i.e. accounts provisioned
via AFT / Account Factory) and store their names + metadata in a JSON file.

Control Tower's `list_managed_accounts` API only returns AccountId and Arn,
not the account name, so we cross-reference AWS Organizations'
`describe_account` to resolve each account's name.

Requires:
    pip install boto3

Credentials:
    Credentials are fetched explicitly (not via env vars or the default
    boto3 credential chain) by shelling out to the rescile vault CLI:
        rescile vault secret get "aws" "AWS_ACCESS_KEY_ID"
        rescile vault secret get "aws" "AWS_SECRET_ACCESS_KEY"
        rescile vault secret get "aws" "AWS_SESSION_TOKEN"
    The resulting values are passed directly into the boto3 Session.
    The credentials used must have permissions for
    controltower:ListManagedAccounts and organizations:DescribeAccount
    (typically in the Control Tower Management account, or a role with
    delegated access).

Usage:
    python get_aft_account_names.py [--region REGION] [--output FILE]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError, BotoCoreError

# Resolve paths relative to this script's location, not the current working
# directory, so the output always lands in the same place regardless of
# where the script is invoked from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "input", "aft_account_names.json"))


def get_vault_secret(key):
    """
    Fetch a single secret value from the rescile vault CLI, e.g.:
        rescile vault secret get "aws" "AWS_ACCESS_KEY_ID"
    Returns the stripped stdout value, or exits with an error if the
    command fails.
    """
    cmd = ["rescile-ce", "vault", "secret", "get", "aws", key]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print(
            "Error: 'rescile' CLI not found on PATH. "
            "Make sure it's installed and accessible.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(
            f"Error: failed to fetch secret '{key}' from rescile vault: "
            f"{e.stderr.strip() if e.stderr else e}",
            file=sys.stderr,
        )
        sys.exit(1)

    value = result.stdout.strip()
    if not value:
        print(f"Error: rescile vault returned an empty value for '{key}'", file=sys.stderr)
        sys.exit(1)
    return value


def get_aws_credentials():
    """Fetch AWS access key, secret key, and session token from the rescile vault."""
    return {
        "aws_access_key_id": get_vault_secret("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": get_vault_secret("AWS_SECRET_ACCESS_KEY"),
        "aws_session_token": get_vault_secret("AWS_SESSION_TOKEN"),
    }


def get_managed_accounts(org_client):
    """
    List all accounts in the Organization using the Organizations API.
    """
    accounts = []
    next_token = None

    while True:
        # Prepare arguments
        kwargs = {}
        if next_token:
            kwargs['NextToken'] = next_token

        # Call the API
        response = org_client.list_accounts(**kwargs)
        accounts.extend(response.get("Accounts", []))

        # Check for more pages
        next_token = response.get("NextToken")
        if not next_token:
            break

    return accounts


def enrich_with_names(org_client, managed_accounts):
    enriched = []
    for acct in managed_accounts:
        # Use 'Id' instead of 'accountId'
        account_id = acct.get("Id")
        entry = {
            "accountId": account_id,
            "arn": acct.get("Arn"),
        }
        try:
            # Note: describe_account also returns data using 'Id' and 'Name'
            details = org_client.describe_account(AccountId=account_id)["Account"]
            entry.update({
                "name": details.get("Name"),
                "email": details.get("Email"),
                "status": details.get("Status"),
                # JoinedTimestamp is a datetime object, handled correctly in your original code
                "joinedTimestamp": details.get("JoinedTimestamp").isoformat()
                                   if details.get("JoinedTimestamp") else None,
            })
        except ClientError as e:
            entry.update({"name": None, "error": f"Error: {e.response['Error']['Code']}"})
        enriched.append(entry)
    return enriched


def main():
    parser = argparse.ArgumentParser(description="Fetch AFT/Control Tower managed account names")
    parser.add_argument("--region", help="AWS region for Control Tower API", default="eu-central-2")
    parser.add_argument(
        "--output",
        help="Output JSON file path (default: ../input/aft_account_names.json relative to script)",
        default=DEFAULT_OUTPUT,
    )
    args = parser.parse_args()

    print("Fetching AWS credentials from rescile vault...")
    credentials = get_aws_credentials()
    session = boto3.Session(**credentials)

    ct_client = session.client("controltower", region_name=args.region)
    org_client = session.client("organizations", region_name=args.region)

    try:
        print(f"Fetching managed accounts from Organizations (region: {args.region})...")
        managed_accounts = get_managed_accounts(org_client)
        print(f"Found {len(managed_accounts)} managed account(s). Resolving names via Organizations...")
        enriched = enrich_with_names(org_client, managed_accounts)
    except (ClientError, BotoCoreError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output = {
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "accountCount": len(enriched),
        "accounts": enriched,
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(enriched)} account(s) to {output_path}")


if __name__ == "__main__":
    main()
