import datetime
import json
from abc import ABC

from common.firms import Firms
from handlers.base_handler import BaseHandler


class TransactionsHandler(BaseHandler, ABC):
    def patch(self, **kwargs):
        try:
            if not self.patch_query_sanity_check(kwargs):
                return
            body = json.loads(self.request.body)
            if not self.body_sanity_check(body):
                return
            self.sql_conn.patch_transaction(_id=kwargs["id"], body=body)
        except Exception as e:
            print("exception")
            self.write(json.dumps({"Status": str(e)}))
            self.set_status(500)
            return

        self.set_status(201)
        self.write(json.dumps({"Status": "ok"}))
        self.finish()

    def post(self, **kwargs):
        try:
            body = json.loads(self.request.body)
            if not self.body_sanity_check(body):
                return
            body["date"] = datetime.datetime.fromisoformat(body["date"])
            transaction_id = self.sql_conn.post_transaction(body)
        except Exception as e:
            self.write(json.dumps({"Status": str(e)}))
            self.set_status(500)
            return

        self.set_status(201)
        self.write(json.dumps({"Status": "ok", "transaction_id": transaction_id}))
        self.finish()

    def get(self, **kwargs):
        self.write(json.dumps([str(i) for i in self.sql_conn.get_transactions()]))

    def patch_query_sanity_check(self, kwargs):
        if not kwargs.get("id", False):
            self.set_status(400)
            self.write("Request's query has to include following keys: "
                       "\"id\": transaction_id")
            self.finish()
            return False
        return True

    def put_body_sanity_check(self, body):
        for i in ["date", "company_name", "price"]:
            if not body.get(i, False):
                self.set_status(400)
                self.write("Request's body has to include at least following keys: \n\"date\": \"yy-MM-dd\", "
                           f"\n\"company_name\": String from the list: {Firms.list_of_companies},"
                           f" \n\"number\": Integer with a number, "
                           f"\n\"operation_type\": Boolean. True - for buying, and False for selling."
                           f"\nThis includes {body} - problem with {i}")
                return False
        return True

    @staticmethod
    def get_handler_url():
        return "transactions/*(?P<id>.*)$"

    @staticmethod
    def get_api_version():
        return 1

    def get_daily_prices(self, days=None):
        """
        The method creates a dictionary, where keys a dates and values a dictionaries {company_name: price}
        :return:  A dictionary, where keys a dates and values a dictionaries {company_name: price}
        """
        info = {}
        prices = self.sql_conn.get_daily_prices(days)
        for price in prices:
            info.setdefault(price.date, {}).setdefault("prices", {})[price.company_name] = price.price
        return info
