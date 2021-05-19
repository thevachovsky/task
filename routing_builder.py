import inspect
import os
from pydoc import locate

from common.base_object import BaseObject
from settings import Settings


class RoutingBuilder(BaseObject):
    """
    A fabric class returning a list of routes basing on a content of 'handlers' module.
    """
    @staticmethod
    def get_url_routing():
        handlers = []
        handlers_folder_path = Settings.get_settings().handlers_root_folder

        # Taking a list of files in 'handlers' folders to use them as modules names.
        # String with file's name is splitted to get filename without a resolution part.
        modules_list = [path.split(".")[0] for path in os.listdir(handlers_folder_path)
                        if os.path.isfile(os.path.join(handlers_folder_path, path))]

        for module_name in modules_list:
            # Taking a module as an object.
            module = locate(f"{handlers_folder_path}.{module_name}")
            for _class_name, _class in inspect.getmembers(module):
                # For every handler creating a tuple with a reference to the class, and url-route based on values
                # returned by the static methods of the class.
                if _class_name.find("Handler") != -1 and not(_class_name in ["BaseHandler", "RequestHandler"]):
                    handlers.append((RoutingBuilder.get_full_url_mask(_class), _class))
        return handlers

    @staticmethod
    def get_full_url_mask(handler_class):
        """
        The method forms url-route basing on common settings and handler's methods
        returning version of API and url part.
        :param handler_class:
        :return:
        """
        url_route =\
            f"/{Settings.get_settings().api_url}/v{handler_class.get_api_version()}/{handler_class.get_handler_url()}"
        print(f"Adding route: {url_route}")
        return url_route

