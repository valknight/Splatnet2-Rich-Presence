import json
import time

# Writes config file and updates the global variables.
def write_config(tokens):
	

	config_file = open("config/config.txt", "w")
	config_file.seek(0)
	config_file.write(json.dumps(tokens, indent=4,
                              sort_keys=True, separators=(',', ': ')))
	config_file.close()

	config_file = open("config/config.txt", "r")
	config_data = json.load(config_file)

	global YOUR_METHOD
	YOUR_METHOD = config_data["method"]
	global SESSION_TOKEN
	SESSION_TOKEN = config_data["session_token"]
	global YOUR_COOKIE
	YOUR_COOKIE = config_data["cookie"]
	global USER_LANG
	USER_LANG = config_data["user_lang"]

	config_file.close()

# Get the data from the config file, and create it if not present
def get_config_file():
    try:
        with open("config/config.txt") as config_f:
            config_data = json.loads(config_f.read())
    except FileNotFoundError:
        config_to_write = {"cookie": "", "friend_code": "",
                           "method": "",  "session_token": "", "user_lang": "en-US"}
        with open("config/config.txt", "w") as config_f:
            config_f.write(json.dumps(config_to_write, indent=4))
        config_data = get_config_file()
    return config_data
