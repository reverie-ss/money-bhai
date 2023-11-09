"""
Generates access token from login code 
"""
import os
import requests
import dotenv
import json

class UpstoxAuthorization:
    """
    To generate the code out of login to upstox, follow the given url
    https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id=<CLIENT_ID>&redirect_uri=https://github.com/reverie-ss/
    Next login into your account and get the authorization code appended to redirect url
    """
    def __init__(self) -> None:
        pass
    
    def update_env_variable(self, access_token: str):
        """
        Updates the acces token environment value
        """
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)

        print("Retrieving access token")
        os.environ["ACCESS_TOKEN"] = access_token

        # Write changes to .env file.
        dotenv.set_key(dotenv_file, "ACCESS_TOKEN", os.environ["ACCESS_TOKEN"])
        dotenv.load_dotenv()
        print("Access token updated")

    def generate_access_token(self, code: str):
        """
        The authorization code can be used only once. You have to generate it again to get new access token

        Response:
        {"email":"ss.saswatsahoo@gmail.com","access_token":"","extended_token":null}
        """

        # Define the API endpoint URL
        url = 'https://api-v2.upstox.com/login/authorization/token'

        # Define the headers
        headers = {
            'accept': 'application/json',
            'Api-Version': '2.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Define the data (request parameters)
        data = {
            'code': code,
            'client_id': os.environ.get("CLIENT_ID"),
            'client_secret': os.environ.get("CLIENT_SECRET"),
            'redirect_uri': os.environ.get("REDIRECT_URI"),
            'grant_type': 'authorization_code',
        }

        # Send a POST request to the API
        response = requests.post(url, headers=headers, data=data)

        # Print the response
        if response.status_code == 200:
            token = json.loads(response.text).get("access_token")
            self.update_env_variable(access_token=token)
        return response
