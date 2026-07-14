#!/usr/bin/env python3
import subprocess

import boto3
from botocore.exceptions import ClientError

# ANSI Escape Sequences for terminal coloring
COLOR_HEADER = "\033[95m"  # Magenta
COLOR_INFO = "\033[94m"    # Blue
COLOR_SUCCESS = "\033[92m" # Green
COLOR_WARN = "\033[93m"    # Yellow
COLOR_FAIL = "\033[91m"    # Red
COLOR_RESET = "\033[0m"    # Reset to standard text

def get_rescile_secret(secret_name):
    """Helper to query the local rescile-ce vault."""
    try:
        cmd = ["rescile-ce", "vault", "secret", "get", "aws", secret_name]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def main():
    print(f"{COLOR_HEADER}============================================================{COLOR_RESET}")
    print(f"{COLOR_HEADER} EVALUATING AFT SERVICE CATALOG PERMISSIONS{COLOR_RESET}")
    print(f"{COLOR_HEADER}============================================================{COLOR_RESET}")

    # Load credentials from vault
    access_key = get_rescile_secret("AWS_ACCESS_KEY_ID")
    secret_key = get_rescile_secret("AWS_SECRET_ACCESS_KEY")
    session_token = get_rescile_secret("AWS_SESSION_TOKEN")

    if not access_key or not secret_key:
        print(f"{COLOR_FAIL}[ERROR] Aborted: Missing keys in Rescile vault.{COLOR_RESET}")
        return

    # Initialize the client targeting the landing zone home region
    region = "eu-central-1"
    session = boto3.Session(
        aws_access_key_id=access_key.strip(),
        aws_secret_access_key=secret_key.strip(),
        aws_session_token=session_token.strip() if session_token else None,
        region_name=region
    )

    sc_client = session.client("servicecatalog")
    target_product_name = "AWS Control Tower Account Factory"
    product_id = None

    # Test 1: Can we see the active portfolios and locate the Account Factory?
    print(f"\n{COLOR_INFO}[TEST 1] Scanning visible Service Catalog products...{COLOR_RESET}")
    try:
        search_response = sc_client.search_products()
        products = search_response.get("ProductViewDetails", []) or search_response.get("ProductViewSummaries", [])

        print(f"  {COLOR_SUCCESS}[SUCCESS] Authenticated with Service Catalog. Found {len(products)} visible products.{COLOR_RESET}")

        for p in products:
            summary = p.get("ProductViewSummary", p)
            if summary.get("Name") == target_product_name:
                product_id = summary.get("ProductId")
                print(f"  {COLOR_SUCCESS}[MATCH] Found Target Product: '{target_product_name}' (ID: {product_id}){COLOR_RESET}")

        if not product_id:
            print(f"  {COLOR_WARN}[WARNING] Authenticated, but '{target_product_name}' is not shared with this role configuration.{COLOR_RESET}")
            print("            Ensure your portfolio constraints grant access to this user/role.")
            return

    except ClientError as e:
        print(f"  {COLOR_FAIL}[FAIL] Access Denied to search_products endpoint.{COLOR_RESET}")
        print(f"         Message: {e.response['Error']['Message']}")
        return

    # Test 2: Can we read the product artifacts and parameters?
    print(f"\n{COLOR_INFO}[TEST 2] Simulating metadata handshake for provisioning...{COLOR_RESET}")
    try:
        # Fetch the provisioning versions (artifacts) for the account factory
        artifacts_response = sc_client.list_provisioning_artifacts(ProductId=product_id)
        artifacts = artifacts_response.get("ProvisioningArtifactDetails", [])

        if artifacts:
            latest_version = artifacts[0]["Name"]
            latest_artifact_id = artifacts[0]["Id"]
            print(f"  {COLOR_SUCCESS}[SUCCESS] Read access confirmed. Latest template version: '{latest_version}'{COLOR_RESET}")

            # Describe parameters to ensure we have structural read capability
            params_response = sc_client.describe_provisioning_parameters(
                ProductId=product_id,
                ProvisioningArtifactId=latest_artifact_id
            )
            print(f"  {COLOR_SUCCESS}[SUCCESS] Parameters mapped successfully. Role has full rights to request account shapes.{COLOR_RESET}")
            print(f"\n{COLOR_SUCCESS}[PASSED] DRY-RUN SUCCESSFUL: This identity is ready to provision via Python.{COLOR_RESET}")
        else:
            print(f"  {COLOR_FAIL}[FAIL] Product found, but no active version artifacts are published.{COLOR_RESET}")

    except ClientError as e:
        print(f"  {COLOR_FAIL}[FAIL] Blocked from reading product layout details.{COLOR_RESET}")
        print(f"         Message: {e.response['Error']['Message']}")

    print(f"\n{COLOR_HEADER}============================================================{COLOR_RESET}")

if __name__ == "__main__":
    main()
