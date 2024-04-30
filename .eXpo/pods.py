from expo import CiscoExpoApi  # make sure expo.py is present in the same folder

api = CiscoExpoApi()

# Access the eXpo
expo = api.get_expo("3jxndaab0pe6s850gju1hgw1q")
print(f"Expo Name: {expo.name}")
if api.choose_datacenter():
    # Create an engagement (replace with your email and demo UID)
    engagement = api.create_engagement()
if engagement:
    print(f"Engagement UID: {engagement.uid}")
    # Set lab environment
    api.set_env(engagement.uid)
