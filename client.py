import datetime
import json
import random
import time

import requests

from common.firms import Firms
from common.operations_types import OperationsTypes


class Client:
    """
    A plain implementation for the servise's client.
    """
    def __init__(self):
        with open("config.json", "r") as config:
            self.global_config = json.load(config)
        self.config = self.global_config["client"]
        self.base_url = self.config["base_url"]
        self.port = self.global_config["port"]
        self.user = self.config["user"]
        self.password = self.config["password"]

    def post_transaction(self, company_name, number, operation_type, date=str(datetime.datetime.now().date())):
        api_version = 1
        body = {
            "company_name": company_name,
            "number": number,
            "operation_type": operation_type,
            "date": date
        }
        endpoint = self.get_url(api_version, "transactions_endpoint")
        response = requests.request(
            method="post", auth=(self.user, self.password), url=endpoint, data=json.dumps(body))
        if response.status_code in [200, 201]:
            print(f"Text: {response.text}")
            return response.json()["transaction_id"]
        print(f"Operation was not successfull: {response.text}")

    def patch_transaction(self, _id, **kwargs):
        api_version = 1
        endpoint = f"{self.get_url(api_version, 'transactions_endpoint')}/{_id}"
        response = requests.request(
            method="patch", auth=(self.user, self.password), url=endpoint, data=json.dumps(kwargs))
        if response.status_code in [200, 201]:
            print(f"Text: {response.text}")
        else:
            print(f"Operation was not successfull: {response.text}")

    def post_price(self, company_name, price, date=str(datetime.datetime.now().date())):
        api_version = 1
        body = {
            "company_name": company_name,
            "price": price,
            "date": date
        }
        endpoint = self.get_url(api_version, "prices_endpoint")
        response = requests.request(
            method="post", auth=(self.user, self.password), url=endpoint, data=json.dumps(body))
        if response.status_code in [200, 201]:
            print(f"Text: {response.text}")
            return response.json()["price_id"]
        print(f"Operation was not successfull: {response.text}")

    def patch_price(self, _id, **kwargs):
        api_version = 1
        endpoint = f"{self.get_url(api_version, 'prices_endpoint')}/{_id}"
        response = requests.request(
            method="patch", auth=(self.user, self.password), url=endpoint, data=json.dumps(kwargs))
        if response.status_code in [200, 201]:
            print(f"Text: {response.text}")
        else:
            print(f"Operation was not successfull: {response.text}")

    def get_url(self, version, endpoint_name):
        return f"{self.base_url}:{self.port}/api/v{version}/{self.config[endpoint_name]}"

    def wait_before_ready(self):
        """
        The method is used to sync the client and the service.
        :return:
        """
        while True:
            time.sleep(1)
            try:
                requests.request(method="get", url=f"{self.base_url}:{self.port}/")
            except Exception:
                print("Backend is not ready")
                continue
            break

    def create_initial_state(self, days_before):
        date = str(datetime.datetime.now().date() - datetime.timedelta(days_before))
        api_version = 1
        endpoint = f"{self.get_url(api_version, 'portfolio_endpoint')}/{date}"
        body = {}
        requests.request(
            method="post", auth=(self.user, self.password), url=endpoint, data=json.dumps(body))

    @staticmethod
    def sample():
        client = Client()
        transaction_id = client.post_transaction(company_name=Firms.Cisco, number=2, operation_type=OperationsTypes.buy)
        client.patch_transaction(_id=transaction_id, company_name=Firms.Acronis, number=4)
        price_id = client.post_price(company_name=Firms.Cisco, price=5)
        client.patch_price(price_id, price=8, company_name=Firms.UnknownSuspiciousCompany)

    @staticmethod
    def data_seeding(days_before):
        def create_random_transaction():
            company_name = Firms.list_of_companies[random.randint(0, companies_number-1)]
            stocks_number = random.randint(0, 10)
            operation_type = OperationsTypes.op_list[random.randint(0, 1)]
            client.post_transaction(company_name=company_name, number=stocks_number, operation_type=operation_type,
                                    date=str(datetime.datetime.now().date()-datetime.timedelta(days=i)))

        def create_random_prices():
            date = str(datetime.datetime.now().date()-datetime.timedelta(days=i))
            for company_name in Firms.list_of_companies:
                client.post_price(company_name=company_name, price=random.randint(0, 10), date=date)

        client = Client()
        client.wait_before_ready()
        client.create_initial_state(days_before)
        companies_number = len(Firms.list_of_companies)
        for i in range(368):
            create_random_transaction()
            create_random_transaction()
            create_random_prices()
