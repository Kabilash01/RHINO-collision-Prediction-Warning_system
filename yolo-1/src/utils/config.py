import os
import yaml

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found.")
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config_data, file)

# Example usage:
# config = Config('path/to/config.yaml')
# print(config.get('some_key'))