import json

class Settings:

    settings = None
    handlers_root_folder = ""
    default_api_version = 0
    api_url = "api"
    dbase_connection_settings = "dbase_connection_settings parameter has not been specified in config.json"

    def set_config(self):
        config = Settings.get_json_config()
        for key in config:
            setattr(Settings.settings, key, config[key])

    @staticmethod
    def get_settings():
        if Settings.settings is None:
            Settings.settings = Settings()
            Settings.settings.set_config()
        return Settings.settings

    @staticmethod
    def get_json_config():
        try:
            with open("config.json", "r") as config_file:
                return json.loads(config_file.read())
        except FileNotFoundError as e:
            raise FileNotFoundError("\n\nConfig file has not been found with a following path: ./config.json. "
                                    "Please check it.")
        except Exception as e:
            raise e