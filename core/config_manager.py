import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                self.settings = json.load(file)
        else:
            self.settings = {'gemini_api_key': '', 'user_settings': {}}
            self.save_settings()

    def save_settings(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def set_api_key(self, api_key):
        self.settings['gemini_api_key'] = api_key
        self.save_settings()

    def get_api_key(self):
        return self.settings['gemini_api_key']

    def update_user_settings(self, **kwargs):
        self.settings['user_settings'].update(kwargs)
        self.save_settings()

    def get_user_settings(self):
        return self.settings['user_settings']
