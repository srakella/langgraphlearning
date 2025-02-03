import requests
import os

class HCPVaultHelper:
    
    def get_api_token():
        hcp_client_id = "CDmeB1wGi1gBvZvpii4EET1M3bLdtCFA"
        hcp_client_secret = "iMv3UzgASKe_f0Yno8AE3fLjk0RkvSNjspQRQqOWrf2h9acTcmzWy9pwq_lnz_4u"
        url = "https://auth.idp.hashicorp.com/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": hcp_client_id,
            "client_secret": hcp_client_secret,
            "grant_type": "client_credentials",
            "audience": "https://api.hashicorp.cloud"
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            hcp_api_token= response.json().get('access_token')
        else:
            hcp_api_token= None
        
        
        
        # Define the URL and the HCP API token
        url = "https://api.cloud.hashicorp.com/secrets/2023-11-28/organizations/dae74dc7-b99a-47bc-9973-7040b16cb42f/projects/a8d51379-af44-45b6-a487-4fcacceaf2d9/apps/mars/secrets:open"
        #hcp_api_token = os.getenv("HCP_API_TOKEN")  # Make sure to set your HCP_API_TOKEN as an environment variable

        # Set up the headers
        headers = {
            "Authorization": f"Bearer {hcp_api_token}"
        }

        # Make the GET request
        response = requests.get(url, headers=headers)
        import json
        # Check if the request was successful
        if response.status_code == 200:
            # Print the formatted JSON response
            data = response.json()
            secrets = data.get('secrets',[])
            if secrets:
                    first_secret = secrets[0]
                    value = first_secret.get('static_version', {}).get('value')
                    return value
            else:
                    return  "No secrets found"
        else:
            return "Failed to retrieve secrets: {response.status_code} - {response.text}"

