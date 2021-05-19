import base64
import datetime
from abc import ABC

from tornado.web import RequestHandler

from common.base_object import BaseObject
from common.firms import Firms
from settings import Settings
from sqlconnector.sql_connector import SQLConnector


class BaseHandler(RequestHandler, BaseObject, ABC):
    """
    The class is used as a parent one for other handlers.
    """

    def prepare(self):
        def auth():
            basic_auth_token = self.request.headers['Authorization'].replace("Basic ", "")
            user, password = base64.b64decode(basic_auth_token).decode("utf-8").split(":")
            if not self.sql_conn.check_user(user=user, password=password) and not (self.request.method != "GET"):
                self.request.full_url()
                self.set_status(401)
                self.write("Unauthorized access")
                self.finish()

        self.sql_conn = SQLConnector()
        if self.request.method != "GET":
            auth()

    def on_finish(self):
        print("I am doing some actions after.")

    def body_sanity_check(self, body):
        """
        The method checks main parameters for compliance with requirements
        :param body:
        :return:
        """
        message = ""
        if body.get("company_name") \
                and (not body["company_name"] in Firms.list_of_companies or not isinstance(body["company_name"], str)):
            message = f"\"company_name\" must be a String from the list: {Firms.list_of_companies}"

        if body.get("date"):
            try:
                date = datetime.date.fromisoformat(body["date"])
            except Exception:
                message = f" Key \"date\" must be a String with the format \"yy-MM-dd\""

        if body.get("number") and not isinstance(body["number"], int):
            message = f"\"number\" must be an Int"

        if body.get("operation_type") and not isinstance(body["operation_type"], bool):
            message = f"\"operation_type\" must be a Boolean. True for buying and False for selling"

        if body.get("price") and not isinstance(body["price"], int):
            message = f"\"price\" must be an Int"

        if message:
            self.write(message)
            self.set_status(400)
            return False
        return True

    def get(self):
        self.write("ready")

    @staticmethod
    def get_handler_url():
        """
        The method returns the last part of url mask used in url-routing. Has to be overridden for every child.
        :return:
        """
        return "/*"

    @staticmethod
    def get_api_version():
        """
        The method returns a version of API a handler belongs to. Has to be overridden for every child.
        :return:
        """
        print(f"Api version for the handler with a name has been set up as '1' as 'get_api_version' "
              f"has not been overridden. It should return a real api version for the handler.")

        return Settings.get_settings().default_api_version
