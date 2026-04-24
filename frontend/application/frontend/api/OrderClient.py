# application/frontend/api/OrderClient.py
import os

from flask import session
import requests


order_service_url = os.environ["ORDER_SERVICE_URL"]

class OrderClient:
    @staticmethod
    def get_order():
        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        url = order_service_url + '/api/order'
        response = requests.request(method="GET", url=url, headers=headers)
        order = response.json()
        return order

    @staticmethod
    def post_add_to_cart(product_id, qty=1):
        payload = {
            'product_id': product_id,
            'qty': qty
        }
        url = order_service_url + '/api/order/add-item'

        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        response = requests.request("POST", url=url, data=payload, headers=headers)
        if response:
            order = response.json()
            return order

    @staticmethod
    def post_checkout():
        url = order_service_url + '/api/order/checkout'

        headers = {
            'Authorization': 'Basic ' + session['user_api_key']
        }
        response = requests.request("POST", url=url, headers=headers)
        order = response.json()
        return order

    @staticmethod
    def get_order_from_session():
        default_order = {
            'items': {},
            'total': 0,
        }
        return session.get('order', default_order)
