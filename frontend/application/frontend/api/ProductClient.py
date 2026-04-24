# application/frontend/api/ProductClient.py
import os

import requests


product_service_url = os.environ["PRODUCT_SERVICE_URL"]

class ProductClient:

    @staticmethod
    def get_products():
        r = requests.get(product_service_url + '/api/products')
        products = r.json()
        return products

    @staticmethod
    def get_product(slug):
        response = requests.request(method="GET", url = product_service_url + '/api/product/' + slug)
        product = response.json()
        return product
