# modules/aft_builder.py

import os
from git import Repo # Requires: pip install gitpython

class AFTBuilder:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def build(self, account_name, email, ou):
        """Generates TF file and pushes to trigger AFT pipeline."""
        tf_filename = f"{account_name}.tf"
        tf_path = os.path.join(self.repo_path, tf_filename)

        tf_content = f"""
module "{account_name}" {{
  source = "github.com/aws-ia/terraform-aws-control_tower_account_factory.git//modules/aft-account-request?ref=main"

  control_tower_parameters = {{
    AccountEmail = "{email}"
    AccountName  = "{account_name}"
    ManagedOrganizationalUnit = "{ou}"
    SSOUserEmail = "{email}"
  }}

  account_tags = {{
    "ManagedBy" = "AFT-Orchestrator"
    "Function"  = "{ou}"
  }}
}}
"""
        with open(tf_path, "w") as f:
            f.write(tf_content)

        # Commit to Git to trigger AFT
        self.repo.index.add([tf_filename])
        self.repo.index.commit(f"Provisioning AFT account: {account_name}")
        self.repo.remotes.origin.push()
        print(f"Committed {tf_filename} to repository.")

    def exists(self, account_name):
        # Check if the file already exists in repo
        return os.path.exists(os.path.join(self.repo_path, f"{account_name}.tf"))
