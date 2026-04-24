# application/order_api/api/UserClient.py
import os

import requests


class UserClient:
    @staticmethod
    def get_user(api_key):
        headers = {
            'Authorization': api_key
        }
        response = requests.request(method="GET", url=os.environ["USER_SERVICE_URL"] + '/api/user', headers=headers)
        if response.status_code == 401:
            return False
        user = response.json()
        return user
