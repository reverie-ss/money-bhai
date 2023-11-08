"""
Generates access token from login code 
"""
import os
import requests

class UpstoxAuthorization:
    """
    To generate the code out of login to upstox, follow the given url
    https://api-v2.upstox.com/login/authorization/dialog?response_type=code&client_id=<CLIENT_ID>&redirect_uri=https://github.com/reverie-ss/
    Next login into your account and get the authorization code appended to redirect url
    """
    def __init__(self) -> None:
        pass

    def generate_access_token(self, code: str):
        """
        The authorization code can be used only once. You have to generate it again to get new access token
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
        print(response.text)
