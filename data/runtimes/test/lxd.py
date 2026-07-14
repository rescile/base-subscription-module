import json
import time

import requests_unixsocket

# Initialize the unix socket session
session = requests_unixsocket.Session()

# LXD API Base URL using the URL-encoded socket path
# %2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket transforms the file path for HTTP
BASE_URL = "http+unix://%2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket/1.0"
VM_NAME = "nicos-vm"

# 1. Define the VM payload
vm_payload = {
    "name": VM_NAME,
    "type": "virtual-machine",
    "source": {
        "type": "image",
        "modes": "pull",
        "server": "https://images.linuxcontainers.org",
        "protocol": "simplestreams",
        "alias": "ubuntu/24.04/cloud"
    },
    "config": {
        "limits.cpu": "2",
        "limits.memory": "4GiB"
    }
}

print(f"🚀 Requesting LXD to create QEMU VM '{VM_NAME}'...")

# 2. Send POST request to create the VM (Async operation)
response = session.post(f"{BASE_URL}/instances", json=vm_payload)
response.raise_for_status()
res_data = response.json()

# Extract the operation ID to track progress
operation_url = f"http+unix://%2Fvar%2Fsnap%2Flxd%2Fcommon%2Flxd%2Funix.socket{res_data['operation']}"

print("⏳ Image pulling and VM creation in progress. Waiting for completion...")

# 3. Poll the operation endpoint until it succeeds
while True:
    op_check = session.get(operation_url).json()
    status = op_check['metadata']['status']

    if status == "Success":
        print("✅ VM successfully created!")
        break
    elif status in ["Failure", "Cancelled"]:
        raise Exception(f"❌ Failed to create VM: {op_check['metadata']['err']}")

    time.sleep(2)  # Check every 2 seconds

# 4. Boot the VM (Change state to 'start')
print(f"⚡ Booting up '{VM_NAME}'...")
start_payload = {"action": "start"}
start_response = session.put(f"{BASE_URL}/instances/{VM_NAME}/state", json=start_payload)
start_response.raise_for_status()

print(f"🎉 QEMU VM '{VM_NAME}' is now running on Nico's machine!")
