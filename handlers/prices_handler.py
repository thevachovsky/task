import json

from common.firms import Firms
from handlers.base_handler import BaseHandler


class PriceHandler(BaseHandler):
    def patch(self, **kwargs):
        try:
            if not self.patch_query_sanity_check(kwargs):
                return
            body = json.loads(self.request.body)
            if not self.body_sanity_check(body):
                return
            self.sql_conn.patch_daily_price(_id=kwargs["id"], body=body)
            self.write(json.dumps({"Status": "ok"}))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"Status":  str(e)}))

    def post(self, **kwargs):
        try:
            body = json.loads(self.request.body)
            if not self.body_sanity_check(body):
                return
            price_id = self.sql_conn.post_daily_price(body)
            self.set_status(201)
            self.write(json.dumps({"Status": "ok", "price_id": price_id}))
        except Exception as e:
            self.write(json.dumps({"Status":  str(e)}))

    def get(self, **kwargs):
        self.write(json.dumps([str(i) for i in self.sql_conn.get_daily_prices()]))

    def patch_query_sanity_check(self, kwargs):
        if not kwargs.get("id", False):
            self.set_status(400)
            self.write("Request's query has to include at least following keys: \"date\": \"yy-MM-dd\", "
                        f"\"company_name\": String from the list: {Firms.list_of_companies}")
            return False
        return True

    def put_body_sanity_check(self, body):
        for i in ["date", "company_name", "price"]:
            if not body.get(i, False):
                self.set_status(400)
                self.write("Request's body has to include at least following keys: \n\"date\": \"yy-MM-dd\", "
                            f"\n\"company_name\": String from the list: {Firms.list_of_companies},"
                            f" \n\"price\": Integer with a price")
                return False
            return True

    @staticmethod
    def get_handler_url():
        return "prices/*(?P<id>.*)"

    @staticmethod
    def get_api_version():
        return 1

    def get_daily_prices(self, days=None):
        '''
        The method creates a dictionary, where keys a dates and values a dictionaries {company_name: price}
        :return:  A dictionary, where keys a dates and values a dictionaries {company_name: price}
        '''
        info = {}
        prices = self.sql_conn.get_daily_prices(days)
        for price in prices:
            info.setdefault(price.date, {}).setdefault("prices", {})[price.company_name] = price.price
        return info

