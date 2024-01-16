#!/usr/bin/env python
"""Hands-On: ISE ANC Policy APIs with Python
   List ISE Adaptive Network Control (ANC) policies.
"""

import sys, os, requests
from pathlib import Path
from pprint import pformat
from crayons import blue, green, white
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Locate the directory containing this file and the repository root.
# Temporarily add these directories to the system path so that we can import
# local files.
here = Path(__file__).parent.absolute()
repository_root = (here / "..").resolve()

sys.path.insert(0, str(repository_root))

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_ise_anc_policies(
    host=os.getenv('ISE_INTERNAL'),
    port="443",
    username="admin",
    password=os.getenv('SESSION_ID'),
):
    """Get a list of configured ISE Adaptive Network Control (ANC) policies."""
    print(blue("\n==> Getting ISE ANC policies"))

    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json"
        }

    authentication = HTTPBasicAuth(username, password)

    response = requests.get(
        f"https://{host}:{port}/ers/config/ancpolicy",
        headers=headers,
        auth=authentication,
        verify=False,
    )
    response.raise_for_status()

    print(green("Successfully retrieved the ANC policies!"))

    return response.json()["SearchResult"]["resources"]


def get_ise_anc_policy_details(
    policy_id,
    host=os.getenv('ISE_INTERNAL'),
    port="443",
    username="admin",
    password=os.getenv('SESSION_ID'),
):
    """Retrieve the details of a configured ANC policy."""
    print(blue(f"\n==> Getting the details for the `{policy_id}` ANC policy"))

    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json"
        }

    authentication = HTTPBasicAuth(username, password)

    response = requests.get(
        f"https://{host}:{port}/ers/config/ancpolicy/{policy_id}",
        headers=headers,
        auth=authentication,
        verify=False,
    )
    response.raise_for_status()

    print(green(f"Successfully retrieved the `{policy_id}`` ANC policy"))

    return response.json()


# If this script is the "main" script, run...
if __name__ == "__main__":
    #TODO : #1 Call the fucntion to get ISE ANC policies assign the value returned by function to "policies" variable
    policies = MISSION
    print(
        white("\nAdaptive Network Control (ANC) Policies:", bold=True),
        pformat(policies),
        sep="\n"
    )
    #TODO: #2 Use the policy/polices you have received from ISE to get the details on the policy.
    devnet_anc_policy = MISSION
    
    #TODO: #3 Print the policy details you have received from ISE 
    print(
        white("\nANC_Devnet Adaptive Network Control Policy:", bold=True),
        pformat(MISSION),
        sep="\n"
    )
