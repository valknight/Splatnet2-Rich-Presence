import json
import requests
import time
import sys
import os
import socket
from config.logger import logger


def get_config_file():
    try:
        with open("config/config.txt") as config_f:
            config_data = json.loads(config_f.read())
    except FileNotFoundError:
        config_to_write = {"api_key": "", "cookie": "", "friend_code": "",
                           "session_token": "skip", "user_lang": ""}
        with open("config/config.txt", "w") as config_f:
            config_f.write(json.dumps(config_to_write, indent=4))
        config_data = get_config_file()
    return config_data


def start_credential_proxy():
    os.system(
        "mitmdump -s ./config/get_session.py -q --set onboarding_host=setup.ink")


class NSOInterface:
    def reload_config(self, config_data=None):
        if config_data is None:
            config_data = get_config_file()
        self.cookie = config_data['cookie']
        return config_data

    def __init__(self, config_data=None):
        config_data = self.reload_config(config_data=config_data)
        # only works with your game region's supported languages
        USER_LANG = config_data["user_lang"]

        if "app_timezone_offset" in config_data:
            app_timezone_offset = str(config_data["app_timezone_offset"])
        else:
            app_timezone_offset = str(int(time.timezone/60))

        if "app_unique_id" in config_data:
            app_unique_id = str(config_data["app_unique_id"])
        else:
            # random 19-20 digit token. used for splatnet store
            app_unique_id = "32449507786579989234"

        if "app_user_agent" in config_data:
            app_user_agent = str(config_data["app_user_agent"])
        else:
            app_user_agent = 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36'

        self.app_head = {
            'Host': 'app.splatoon2.nintendo.net',
            'x-unique-id': app_unique_id,
            'x-requested-with': 'XMLHttpRequest',
            'x-timezone-offset': app_timezone_offset,
            'User-Agent': app_user_agent,
            'Accept': '*/*',
            'Referer': 'https://app.splatoon2.nintendo.net/home',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': USER_LANG
        }

    def gen_new_cookie(self, reason):
        logger.warn(
            "Cookie invalid - reason: {} - loading proxy to regenerate".format(reason))
        logger.info("In order to get a new token, we need to intercept it from the real NSO app. Please make sure you have a smartphone or Android emulator to continue.")
        logger.info(
            "If your smartphone runs Android 7.0 or higher, you will need to use an Android emulator or an iOS device to continue.")
        start_credential_proxy()

    def load_json(self, bool):
        '''Returns results JSON from online.'''

        if bool:
            # grab data from SplatNet 2
            logger.debug("Pulling data from online...")
        url = "https://app.splatoon2.nintendo.net/api/results"
        results_list = requests.get(
            url, headers=self.app_head, cookies=dict(iksm_session=self.cookie))
        return json.loads(results_list.text)

    def load_results(self, calledby=""):
        '''Returns the data we need from the results JSON, if possible.'''

        data = self.load_json(False)
        try:
            results = data["results"]  # all we care about
        except KeyError:
            if self.cookie == "":
                reason = "blank"
            elif data["code"] == "AUTHENTICATION_ERROR":
                reason = "auth"
            else:
                reason = "other"  # server error or player hasn't battled before
            self.gen_new_cookie(reason)
            data = self.load_json(False)

            # we do this just so that we don't end up using the old, borked up token
            self.reload_config()

            # try again with correct tokens; shouldn't get an error now...
            results = self.load_results()

        return results
