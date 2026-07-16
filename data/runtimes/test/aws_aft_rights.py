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

def check_service_catalog_access(sc_client):
    print(f"\n{COLOR_INFO}[DIAGNOSTIC] Checking raw Portfolio visibility...{COLOR_RESET}")
    try:
        portfolios = sc_client.list_portfolios()
        details = portfolios.get('PortfolioDetails', [])
        print(f"  {COLOR_SUCCESS}Visible Portfolios: {len(details)}{COLOR_RESET}")
        for p in details:
            print(f"   - {p['DisplayName']} (ID: {p['Id']})")
    except ClientError as e:
        print(f"  {COLOR_FAIL}list_portfolios error: {e.response['Error']['Message']}{COLOR_RESET}")

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
    region = "eu-central-2"
    session = boto3.Session(
        aws_access_key_id=access_key.strip(),
        aws_secret_access_key=secret_key.strip(),
        aws_session_token=session_token.strip() if session_token else None,
        region_name=region
    )

    sc_client = session.client("servicecatalog")

    sts_client = session.client("sts")
    identity = sts_client.get_caller_identity()
    print(f"\n{COLOR_INFO}[DIAGNOSTIC] Script executing as: {identity['Arn']}{COLOR_RESET}")

    check_service_catalog_access(sc_client)

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

    # Test 2: Dynamischer Metadata Handshake
    print(f"\n{COLOR_INFO}[TEST 2] Simulating metadata handshake for provisioning...{COLOR_RESET}")
    try:
        # 1. Launch Path holen
        paths = sc_client.list_launch_paths(ProductId=product_id)
        if not paths.get('LaunchPathSummaries'):
            print(f"  {COLOR_FAIL}[FAIL] Kein Launch Path für dieses Produkt gefunden.{COLOR_RESET}")
            return
        path_id = paths['LaunchPathSummaries'][0]['Id']

        # 2. Dynamisch das neueste, aktive Artifact finden
        artifacts = sc_client.list_provisioning_artifacts(ProductId=product_id)
        active_artifacts = [a for a in artifacts.get("ProvisioningArtifactDetails", []) if a.get("Active")]

        if not active_artifacts:
            print(f"  {COLOR_FAIL}[FAIL] Keine aktiven Artifacts für dieses Produkt gefunden.{COLOR_RESET}")
            return

        # Nimm das neueste (normalerweise das erste in der Liste)
        latest_artifact = active_artifacts[0]
        latest_artifact_id = latest_artifact["Id"]
        print(f"  {COLOR_SUCCESS}[SUCCESS] Dynamisch gelöstes Artifact: {latest_artifact['Name']} (ID: {latest_artifact_id}){COLOR_RESET}")

        # 3. Parameter abrufen
        params_response = sc_client.describe_provisioning_parameters(
            ProductId=product_id,
            ProvisioningArtifactId=latest_artifact_id,
            PathId=path_id
        )
        print(f"  {COLOR_SUCCESS}[SUCCESS] Parameter erfolgreich geladen.{COLOR_RESET}")
        print(f"\n{COLOR_SUCCESS}[PASSED] DRY-RUN SUCCESSFUL: Bereit zur Provisionierung.{COLOR_RESET}")

    except ClientError as e:
        print(f"  {COLOR_FAIL}[FAIL] API Error: {e.response['Error']['Message']}{COLOR_RESET}")

    print(f"\n{COLOR_HEADER}============================================================{COLOR_RESET}")

if __name__ == "__main__":
    main()
