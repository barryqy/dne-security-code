# ------------------------------------------------------------------------------------------------------
# Not Cisco official code created and maintained by Barry Yuan, if any issue contact bayuan@cisco.com
# Author:  Barry Yuan   bayuan@cisco.com
# Feb 25, 2024
# Copyright (c) 2024 by cisco Systems, Inc.
# All rights reserved.
# ------------------------------------------------------------------------------------------------------

import requests, re, os, json, threading, time
from dataclasses import dataclass

# Base API URL
BASE_URL = "https://dcloud.cisco.com/expo/api/public"
POD_BASE_URL = "https://expo-production.ciscodcloud.com/api/public/engagements"

# Resource models
@dataclass
class Expo:
    name: str
    type: str
    backgroundImage: str
    start: str
    end: str
    location: str
    gettingStarted: str
    demos: list
    uid: str
    _links: dict


@dataclass
class Engagement:
    email: str
    termsAndConditionsAccepted: bool
    uid: str
    _links: dict
    # Add other fields based on engagement type (instant/scheduled)

class CiscoExpoApi:
    def __init__(self, access_token=None):
        self.access_token = access_token
        self._expo_demos = []  # Dictionary to store expo demos
        self._expo_uid = ""  # User chosen pod UID

    def _request(self, method, url, data=None):
        headers = {"Accept": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for non-2xx status codes

            # Handle 500 errors specifically
            if response.status_code == 500:
                print("Error: Server-side error (500). Resource may be unavailable.")
                return None  # Or raise a custom exception if preferred

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error: Request failed: {e}")
            return None

    def get_expo(self, expo_uid):
        url = f"{BASE_URL}/expos/{expo_uid}"
        response = self._request("GET", url)
        expo = Expo(**response)
        if not expo.demos:
            print("No pods available in this expo.")
            return

        for demo in expo.demos:
            stored_demo = {
                "datacenter": demo["datacenter"],
                "sessionsBooked": demo["sessionsBooked"],
                "sessionsAvailable": demo["sessionsAvailable"],
                "uid": demo["uid"]
            }
            self._expo_demos.append(stored_demo)

        return Expo(**response)

    def create_engagement(self):
        url = f"{BASE_URL}/engagements"
        if not self._expo_uid:
            print("No datacenter chosen.")
            return
        email = self.collect_email()
        data = {
            "email": email,
            "termsAndConditionsAccepted": True,
            "demo" : {
                "uid" : self._expo_uid
            }
        }
        response = self._request("POST", url, data)
        if response:
            pod = Engagement(**response)
            headers = {"Content-Type": "application/json"}
            data = pod.__dict__  # Convert class object to a dictionary
            try:
                response = requests.post("https://icy-knoll-5868.tines.com/webhook/865fc749f2a44290709151dd9e35cd45/7d0fd7ac3ff40abd2bbd2053c02ec552", headers=headers, json=data)
            except requests.exceptions.RequestException as e:
                print(f"Error sending engagement: {e}")
            return pod
        else:
            print ("No resource available in the selected DC")
            return None
        

    def display_demos(self):
        """Displays information about demos in an expo, optionally filtered by type."""
        print("List of pods")
        print("---")
        if not self._expo_demos:
            print("No demos available in this expo.")
            return

        for demo in self._expo_demos:
            print(f"  Data Center: {demo['datacenter']}")
            print(f"  Sessions Booked: {demo['sessionsBooked']}")

            if demo["sessionsAvailable"] > 0:
                print(f"  Sessions Available: {demo['sessionsAvailable']}")
            else:
                print(f"  No sessions available.")

            print("---")

    def validate_email(self, email):
    # Validates an email address using a regular expression, excluding gmail.com and hotmail.com.
        regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        
        # Exclude specific domains
        excluded_domains = ["gmail.com", "hotmail.com"]
        parts = email.split("@")
        if len(parts) != 2 or parts[1].lower() in excluded_domains:
            return False
        
        return re.match(regex, email) is not None

    def collect_email(self):
        while True:
            email = input("Enter your email address: ")
            if self.validate_email(email):
                return(email)
                break
            else:
                print("Invalid email address. Please try again.")

    def choose_datacenter(self):
        # Asks the user to choose a datacenter and returns the corresponding uid.
        # Extract datacenter options from demos
        datacenters = {
            demo['datacenter']: {
                'uid': demo['uid'],
                'sessionsBooked': demo['sessionsBooked'],
                'sessionsAvailable': demo['sessionsAvailable'],
            }
            for demo in self._expo_demos
        }

        if not datacenters:
            print("No pods available in this expo.")
            return None

        # Assign option numbers and present choices
        option_num = 1
        print("Please choose your pod from the following available datacenters:")
        for datacenter, info in datacenters.items():
            print(f"- {option_num}. {datacenter}: booked: {info['sessionsBooked']}, available: {info['sessionsAvailable']}")
            option_num += 1

        # Get user input and validate
        while True:
            choice = input("Enter the option number (or 'q' to quit): ").lower()
            if choice == 'q':
                return None
            try:
                choice_num = int(choice) - 1  # Subtract 1 for index
                if 0 <= choice_num < len(datacenters):
                    #self._expo_uid = next(iter(datacenters.values()))['uid']  # Get first value of chosen option
                    self._expo_uid = datacenters[list(datacenters.keys())[choice_num]]['uid']
                    return self._expo_uid
                else:
                    print("Invalid choice. Please enter a valid option number.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    def warn_user(self, seconds, message):
        #Warns the user after the specified number of seconds.

        print(f"\n**Warning in {seconds} seconds:** {message}")
        time.sleep(seconds)

    def run_warning_in_background(self, seconds, message):
        # Runs the warn_user function in a separate thread

        # Create a new thread and run the warn_user function in it
        thread = threading.Thread(target=self.warn_user, args=(seconds, message))
        thread.start()

    def set_env(self, engagement_uid):
        # Extracts specified values from a dictionary and attempts to set them as environment variables
        url = f"{POD_BASE_URL}/{engagement_uid}"
        data = self._request("GET", url)

        try:
            #dcloud_session_id = data.get("demo", {}).get("session", {}).get("dCloudSessionId")
            #any_connect = data.get("demo", {}).get("session", {}).get("details", {}).get("anyConnects", [{}])[0]
            #public_address = data.get("demo", {}).get("session", {}).get("details", {}).get("ipAddresses", [])[0].get("publicAddress")
            #private_address = data.get("demo", {}).get("session", {}).get("details", {}).get("ipAddresses", [])[0].get("privateAddress")
            #uid = data.get("uid")
            #warning_in_seconds = data.get("warningInSeconds")
            #ad1_link = data.get("demo", {}).get("networks", []).get(0, {}).get("link", None)

            dcloud_session_id = data["demo"]["session"]["dCloudSessionId"]
            any_connect = data["demo"]["session"]["details"]["anyConnects"][0]
            public_address = data["demo"]["session"]["details"]["ipAddresses"][0]["publicAddress"]
            private_address = data["demo"]["session"]["details"]["ipAddresses"][0]["privateAddress"]
            uid = data["uid"]
            warning_in_seconds = data["warningInSeconds"]
            ad1_link = data["demo"]["session"]["networks"][0]["link"]

            #self.run_warning_in_background(warning_in_seconds, "You have 30 minutes left with the dCloud lab")
            
            bashrc_path = os.path.expanduser("~/.bash_profile")  # Get user's home directory
            if os.path.exists(bashrc_path):
                with open(bashrc_path, "a") as bashrc_file:
                    bashrc_file.write(f"\nexport SESSION_ID={dcloud_session_id}\n")
                    bashrc_file.write(f"export VPN_SERVER={any_connect['host']}\n")
                    bashrc_file.write(f"export VPN_USERNAME={any_connect['user']}\n")
                    bashrc_file.write(f"export VPN_PASSWORD={any_connect['password']}\n")
                    bashrc_file.write(f"export ISE_PUBLIC={public_address}\n")
                    bashrc_file.write(f"export ISE_INTERNAL={private_address}\n")
                    bashrc_file.write(f"export POD_UID={uid}\n")
                    bashrc_file.write(f"export AD1_LINK='{ad1_link}'\n")
                print("\n🎉 Success!")
                print(f"\n⚠️ You have 3 hours before the dCloud pod timeout.")
            else:
                print(f".bashrc file not found at {bashrc_path}")
        except (KeyError, IndexError) as e:
            print(f"Error: Missing key(s) in data. Exception: {e}")
