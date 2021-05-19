import tornado.web
import tornado.ioloop
import threading

from client import Client
from routing_builder import RoutingBuilder
from sqlconnector.sql_connector import SQLConnector

def data_seeding():
    Client.data_seeding(days_before=377)
    print("\n\n\nData seeding has been completed.")


if __name__ == "__main__":
    routes = RoutingBuilder.get_url_routing()
    app = tornado.web.Application(routes)
    app.listen(8080)
    SQLConnector.seed_users()
    threading.Thread(target=data_seeding).start()
    tornado.ioloop.IOLoop.current().start()