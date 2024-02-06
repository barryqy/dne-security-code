#!/usr/bin/env python
"""Mission: Quarantine rogue endpoints with ISE
   Option challenge, if you choose to accept it
"""

import json, sys, os, requests
from pathlib import Path
from crayons import blue, green, red
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# Locate the directory containing this file and the repository root.
# Temporarily add these directories to the system path so that we can import
# local files.
here = Path(__file__).parent.absolute()
repository_root = (here / ".." / "..").resolve()

sys.path.insert(0, str(repository_root))

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Functions

def createPayload(maclist, policy):
    data_to_send = {
        'OperationAdditionalData': {
            'additionalData' : [{
                'name': 'macAddress',
                f'value': maclist
                },
                {
                    'name': 'policyName',
                    f'value': policy
                    }]
        }
    }
    return data_to_send


def readmacaddr_file(filename) :
    with open (filename, 'r') as fp:
        maclist = json.loads(fp.read())
    return maclist

headers = {
    'content-type': "application/json",
    'accept': "application/json"
    }
username = "admin"
password = os.getenv('SESSION_ID')
host = os.getenv('ISE_INTERNAL')
port = "443"


def get_policy_ise():

    #TODO: #1 Create the URL for the GET request to get the ANC policy from ISE. Hint: Make sure you pass the Auth paramenters for the API call
    url = MISSION

    #Create GET Request
    req = requests.get(url, verify=False, headers=headers)
    #req = requests.request("GET", url, verify=False, headers=headers)
    namelist = " "
    if(req.status_code == 200):
        resp_json = req.json()
        policies = resp_json["SearchResult"]["resources"]
        for policy in policies:
            namelist = policy["name"]
            print("\nI've Found the Quarantine Policy {0} to Nuke the Rogue computers from the corp network... \n".format(namelist) )
    else:
        print("An error has ocurred with the following code %(error)s" % {'error': req.status_code})
    return namelist

def post_to_ise(maclist, namelist):
    #TODO: #2 Create the URL for the PUT request to apply the ANC policy! Hint: Make sure you pass the Auth paramenters for the API call
    url = MISSION
    
    for items in maclist:
        payload = "{\r\n    \"OperationAdditionalData\": {\r\n    \"additionalData\": [{\r\n    \"name\": \"macAddress\",\r\n    \"value\": \""+ items + "\"\r\n    },\r\n    {\r\n    \"name\": \"policyName\",\r\n    \"value\": \"" + namelist + '"' + "\r\n    }]\r\n  }\r\n}"
        print(json.dumps(payload,sort_keys=True,indent=3))
        response = requests.request("PUT", url, data=payload, verify=False, headers=headers)
        if(response.status_code == 204):
            print("Done!..Applied Quarantine policy to the rogue endpoint...MAC: {0} Threat is now contained....".format(items))
            success = True
        else:
            print("An error has ocurred with the following code %(error)s" % {'error': response.status_code})
            success = False
    return success

if __name__ == "__main__":
   maclist_path = repository_root / "mission-data/mac-addresses.json"
   maclist = readmacaddr_file(maclist_path)

   #TODO #3 Call the function for getting ANC policy and store it in the policylist variable
   policylist = MISSION
   
   #TODO #4 Call the function for applying policy to the endpoints
   result = MISSION
   
   # # if no errors, Display Mission Completed
   if result:
     print(green("ISE Mission Completed!!!"))
   else:
     print(red("Please check the errors above and troubleshoot"))
