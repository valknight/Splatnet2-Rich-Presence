from __future__ import print_function
from config.logger import logger
from builtins import input

import json
import requests
import time
import sys
import re
import os
import socket, config_functions
import base64, hashlib
import uuid, time, random, string


A_VERSION = "1.5.1"
session = requests.Session()

# Log into a Nintendo Account and return a Session Token
def log_in(ver):

	global version
	version = ver

	auth_state = base64.urlsafe_b64encode(os.urandom(36))

	auth_code_verifier = base64.urlsafe_b64encode(os.urandom(32))
	auth_cv_hash = hashlib.sha256()
	auth_cv_hash.update(auth_code_verifier.replace(b"=", b""))
	auth_code_challenge = base64.urlsafe_b64encode(auth_cv_hash.digest())

	app_head = {
		'Host':                      'accounts.nintendo.com',
		'Connection':                'keep-alive',
		'Cache-Control':             'max-age=0',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent':                'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
		'Accept':                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n',
		'DNT':                       '1',
		'Accept-Encoding':           'gzip,deflate,br',
	}

	body = {
		'state':                               auth_state,
		'redirect_uri':                        'npf71b963c1b7b6d119://auth',
		'client_id':                           '71b963c1b7b6d119',
		'scope':                               'openid user user.birthday user.mii user.screenName',
		'response_type':                       'session_token_code',
		'session_token_code_challenge':        auth_code_challenge.replace(b"=", b""),
		'session_token_code_challenge_method': 'S256',
		'theme':                               'login_form'
	}

	url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
	r = session.get(url, headers=app_head, params=body)

	post_login = r.history[0].url

	print("\nNavigate to this URL in your browser:")
	print(post_login)
	print("Log in, right click the \"Select this person\" button, copy the link address, and paste it below:")

	while True:
		try:
			use_account_url = input("")
			session_token_code = re.search('de=(.*)&', use_account_url)
			return get_session_token(session_token_code.group(1), auth_code_verifier)
		except KeyboardInterrupt:
			print("\nBye!")
			sys.exit(1)
		except:
			print("Malformed URL. Please try again, or press Ctrl+C to exit.")
			print("URL:", end=' ')

# Retrieves the Session Token from log_in URL
def get_session_token(session_token_code, auth_code_verifier):
	
	app_head = {
		'User-Agent':      'OnlineLounge/1.5.0 NASDKAPI Android',
		'Accept-Language': 'en-US',
		'Accept':          'application/json',
		'Content-Type':    'application/x-www-form-urlencoded',
		'Content-Length':  '540',
		'Host':            'accounts.nintendo.com',
		'Connection':      'Keep-Alive',
		'Accept-Encoding': 'gzip'
	}

	body = {
		'client_id':                   '71b963c1b7b6d119',
		'session_token_code':          session_token_code,
		'session_token_code_verifier': auth_code_verifier.replace(b"=", b"")
	}

	url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'

	r = session.post(url, headers=app_head, data=body)
	return json.loads(r.text)["session_token"]

# Retrieves Auto-Cookie with session_token and userLang
def get_cookie(session_token, userLang, ver):

	global version
	version = ver

	timestamp = int(time.time())
	guid = str(uuid.uuid4())

	app_head = {
		'Host':            'accounts.nintendo.com',
		'Accept-Encoding': 'gzip',
		'Content-Type':    'application/json; charset=utf-8',
		'Accept-Language': userLang,
		'Content-Length':  '437',
		'Accept':          'application/json',
		'Connection':      'Keep-Alive',
		'User-Agent':      'OnlineLounge/1.5.0 NASDKAPI Android'
	}

	body = {
		'client_id':     '71b963c1b7b6d119',  # Splatoon 2 service
		'session_token': session_token,
		'grant_type':    'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token'
	}

	url = "https://accounts.nintendo.com/connect/1.0.0/api/token"

	r = requests.post(url, headers=app_head, json=body)
	id_response = json.loads(r.text)

	# get user info
	try:
		app_head = {
			'User-Agent':      'OnlineLounge/1.5.0 NASDKAPI Android',
			'Accept-Language': userLang,
			'Accept':          'application/json',
			'Authorization':   'Bearer {}'.format(id_response["access_token"]),
			'Host':            'api.accounts.nintendo.com',
			'Connection':      'Keep-Alive',
			'Accept-Encoding': 'gzip'
		}
	except:
		print("Not a valid authorization request. Please delete config.txt and try again.")
		print("Error from Nintendo (in api/token step):")
		print(json.dumps(id_response, indent=2))
		sys.exit(1)
	url = "https://api.accounts.nintendo.com/2.0.0/users/me"

	r = requests.get(url, headers=app_head)
	user_info = json.loads(r.text)

	nickname = user_info["nickname"]

	# get access token
	app_head = {
		'Host':             'api-lp1.znc.srv.nintendo.net',
		'Accept-Language':  userLang,
		'User-Agent':       'com.nintendo.znca/1.5.0 (Android/7.1.2)',
		'Accept':           'application/json',
		'X-ProductVersion': '1.5.0',
		'Content-Type':     'application/json; charset=utf-8',
		'Connection':       'Keep-Alive',
		'Authorization':    'Bearer',
		'Content-Length':   '1036',
		'X-Platform':       'Android',
		'Accept-Encoding':  'gzip'
	}

	body = {}
	try:
		idToken = id_response["id_token"]

		flapg_response = call_flapg_api(idToken, guid, timestamp)
		flapg_nso = flapg_response["login_nso"]
		flapg_app = flapg_response["login_app"]

		parameter = {
			'f':          flapg_nso["f"],
			'naIdToken':  flapg_nso["p1"],
			'timestamp':  flapg_nso["p2"],
			'requestId':  flapg_nso["p3"],
			'naCountry':  user_info["country"],
			'naBirthday': user_info["birthday"],
			'language':   user_info["language"]
		}
	except SystemExit:
		sys.exit(1)
	except:
		print("Error(s) from Nintendo:")
		print(json.dumps(id_response, indent=2))
		print(json.dumps(user_info, indent=2))
		sys.exit(1)
	body["parameter"] = parameter

	url = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"

	r = requests.post(url, headers=app_head, json=body)
	splatoon_token = json.loads(r.text)

	# Get Splatoon Access token
	try:
		app_head = {
			'Host':             'api-lp1.znc.srv.nintendo.net',
			'User-Agent':       'com.nintendo.znca/1.5.0 (Android/7.1.2)',
			'Accept':           'application/json',
			'X-ProductVersion': '1.5.0',
			'Content-Type':     'application/json; charset=utf-8',
			'Connection':       'Keep-Alive',
			'Authorization':    'Bearer {}'.format(splatoon_token["result"]["webApiServerCredential"]["accessToken"]),
			'Content-Length':   '37',
			'X-Platform':       'Android',
			'Accept-Encoding':  'gzip'
		}
	except:
		print("Error from Nintendo (in Account/Login step):")
		print(json.dumps(splatoon_token, indent=2))
		sys.exit(1)

	body = {}
	parameter = {
		'id':                5741031244955648,
		'f':                 flapg_app["f"],
		'registrationToken': flapg_app["p1"],
		'timestamp':         flapg_app["p2"],
		'requestId':         flapg_app["p3"]
	}
	body["parameter"] = parameter

	url = "https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken"

	r = requests.post(url, headers=app_head, json=body)
	splatoon_access_token = json.loads(r.text)

	# Get Auto-Cookie
	try:
		app_head = {
			'Host':                    'app.splatoon2.nintendo.net',
			'X-IsAppAnalyticsOptedIn': 'false',
			'Accept':                  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding':         'gzip,deflate',
			'X-GameWebToken':          splatoon_access_token["result"]["accessToken"],
			'Accept-Language':         userLang,
			'X-IsAnalyticsOptedIn':    'false',
			'Connection':              'keep-alive',
			'DNT':                     '0',
			'User-Agent':              'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
			'X-Requested-With':        'com.nintendo.znca'
		}
	except:
		print("Error from Nintendo (in Game/GetWebServiceToken step):")
		print(json.dumps(splatoon_access_token, indent=2))
		sys.exit(1)

	url = "https://app.splatoon2.nintendo.net/?lang={}".format(userLang)
	r = requests.get(url, headers=app_head)
	return nickname, r.cookies["iksm_session"]

# Passes an id_token and timestamp to the s2s API and fetches the resultant hash from the response.
def get_hash_from_s2s_api(id_token, timestamp):

	# Check to make sure we're allowed to contact the API.
	config_file = open("config/config.txt", "r")
	config_data = json.load(config_file)
	config_file.close()
	try:
		num_errors = config_data["api_errors"]
	except:
		num_errors = 0

	if num_errors >= 5:
		print("Too many errors received from the splatnet2statink API. Further requests have been blocked until the \"api_errors\" line is manually removed from config.txt. If this issue persists, please contact @frozenpandaman on Twitter/GitHub for assistance.")
		sys.exit(1)

	# Proceed normally
	try:
		api_app_head = {'User-Agent': "splatnet2statink/{}".format(version)}
		api_body = {'naIdToken': id_token, 'timestamp': timestamp}
		api_response = requests.post(
			"https://elifessler.com/s2s/api/gen2", headers=api_app_head, data=api_body)
		return json.loads(api_response.text)["hash"]
	except:
		print("Error from the splatnet2statink API:\n{}".format(
			json.dumps(json.loads(api_response.text), indent=2)))

		# Add 1 to api_errors in config
		config_file = open("config/config.txt", "r")
		config_data = json.load(config_file)
		config_file.close()
		try:
			num_errors = config_data["api_errors"]
		except:
			num_errors = 0
		num_errors += 1
		config_data["api_errors"] = num_errors

		config_file = open("config/config.txt", "w")  # from write_config()
		config_file.seek(0)
		config_file.write(json.dumps(config_data, indent=4,
                               sort_keys=True, separators=(',', ': ')))
		config_file.close()

		sys.exit(1)

# Passes in headers to the flapg API (Android emulator) and fetches the response.
def call_flapg_api(id_token, guid, timestamp):
	
	try:
		api_app_head = {
			'x-token': id_token,
			'x-time':  str(timestamp),
			'x-guid':  guid,
			'x-hash':  get_hash_from_s2s_api(id_token, timestamp),
			'x-ver':   '2',
			'x-iid':   ''.join([random.choice(string.ascii_letters + string.digits) for n in range(8)])
		}
		api_response = requests.get(
			"https://flapg.com/ika2/api/login", headers=api_app_head)
		f = json.loads(api_response.text)
		return f

	except:
		try:  # if api_response never gets set
			if api_response.text:
				print(u"Error from the flapg API:\n{}".format(json.dumps(
					json.loads(api_response.text), indent=2, ensure_ascii=False)))
			elif api_response.status_code == requests.codes.not_found:
				print("Error from the flapg API: Error 404 (offline or incorrect headers).")
			else:
				print("Error from the flapg API: Error {}.".format(api_response.status_code))
		except:
			pass
		sys.exit(1)

# When User wants to retrieve Cookie Manually
def start_credential_proxy():
    status_code = os.system(
        "mitmdump -s ./config/get_session.py -q --set onboarding_host=setup.ink")
    
    if bool(status_code):
        sys.exit(1)
    else: 
        config_data = config_functions.get_config_file()
        YOUR_COOKIE = config_data["cookie"]
        return YOUR_COOKIE


class NSOInterface:

	# Reload the config, such as after the cookie has changed
    def reload_config(self, config_data=None):
        if config_data is None:
            config_data = config_functions.get_config_file()
        self.cookie = config_data['cookie']
        return config_data

    def __init__(self, config_data=None):
        config_data = self.reload_config(config_data=None)
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
            app_unique_id = "46674186337252616651"

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

	# Attempts to generate a new cookie in case the provided one is invalid
    def gen_new_cookie(self, reason):
        
        new_cookie = ""
        manual = False

        config_data = self.reload_config(config_data=None)
        SESSION_TOKEN = config_data["session_token"]
        USER_LANG     = config_data["user_lang"]
        
        if reason == "blank":
            print("There is no Cookie stored in yet")
            
        elif reason == "auth":  # authentication error
            print("The stored Cookie has expired.")

        else:  # server error or player hasn't battled before
            print("Cannot access SplatNet 2 without having played at least one battle online.")
            sys.exit(1)


        ## SESSION TOKEN CHECKER ##
        # If SESSION_TOKEN is empty
        if SESSION_TOKEN == "":
            print("session_token is blank. Please log in to your Nintendo Account to obtain your session_token.")
            new_token = log_in(A_VERSION)
            if new_token == None:
                print("There was a problem logging you in. Please try again later.")
            else:
                if new_token == "skip":  
                    manual = True
                    print("\nYou have opted against Automatic Cookie Generation.\n")
                else:
                    print("\nWrote session_token to config.txt.")
                config_data["session_token"] = new_token
                config_functions.write_config(config_data)

        # If SESSION_TOKEN is skip (For retrieving the Cookie Manually)
        elif config_data["session_token"] == "skip":
            manual = True
            print("\nYou have opted against Automatic Cookie Generation. Using the Manual Cookie Generation Function\n")
        
        
        # If Manual is set to True
        if manual:
            # Starts proxy to get new cookie from a user
	        logger.warn("Cookie invalid - reason: {} - loading proxy to regenerate".format(reason))
	        logger.info("In order to get a new token, we need to intercept it from the real NSO app. Please make sure you have a smartphone or Android Emulator (Nox) to continue.")
	        logger.info("If your smartphone runs Android 7.0 or higher, you will need to use an Android Emulator (Nox) or an iOS device to continue.")
	        new_cookie = start_credential_proxy()

        # If Manual is still set on False
        else:
            SESSION_TOKEN = config_data["session_token"]
            print("Attempting to generate new cookie...")          
            acc_name, new_cookie = get_cookie(SESSION_TOKEN, USER_LANG, A_VERSION)

        config_data["cookie"] = new_cookie
        config_functions.write_config(config_data)
        
        if manual:
            print("Wrote iksm_session cookie to config.txt.")

        else:
            print("Wrote iksm_session cookie for {} to config.txt.".format(acc_name))

        return config_data["cookie"]

	# Returns results JSON from online.
    def load_json(self, api_method):
        url = "https://app.splatoon2.nintendo.net/api/{}".format(api_method)
        logger.debug("Pulling data from {}".format(url))
        results_list = requests.get(
            url, headers=self.app_head, cookies=dict(iksm_session=self.cookie))
        results_data = json.loads(results_list.text)
        return results_data

	# Returns the data we need from the results JSON, if possible
    def load_results(self, calledby="", salmonrun=True):
        '''
			Params:
			salmonrun - Set to false if you don't want to merge in salmonrun data
		'''
        
        data = self.load_json("results")
        config_data = self.reload_config(config_data=None)
        YOUR_COOKIE = config_data["cookie"]

        # Checks if there are results coming from the API
        # If there are results coming
        try:
            results = data["results"]  # all we care about
            

        # If there are no results coming
        except KeyError:

            # If YOUR_COOKIE is empty
            if YOUR_COOKIE == "":
                reason = "blank"
            
            # If there's an Authentication Error
            elif data["code"] == "AUTHENTICATION_ERROR":
                reason = "auth"

            # If there's another Error
            else:
                reason = "other"  # server error or player hasn't battled before

            # Pass reason to gen.new_cookie() function
            self.gen_new_cookie(reason)

            # Try to retrieve the Results from the API again after the Cookie Retrieving process
            config_data1 = self.reload_config(config_data=None)
            YOUR_COOKIE = config_data1["cookie"]
            
            data = self.load_json("results")
            
            # If there are finally results coming (Correct Tokens)
            try:
                results = data["results"]
                logger.info(
                    "The Rich Presence is running, check your Discord Profile. Enjoy!")

            # If there are still no results coming (Cause there are no Online Battles availabe to be fetched)
            except:
                print("Cannot access SplatNet 2 without having played at least one battle online.")
                sys.exit(1)

        if salmonrun:

            # Assigning salmonrun_data with SR JSON
            salmonrun_data = self.load_json("coop_results")

            # Assigning coop_match with the most recent played Salmon Run Match
            coop_match = salmonrun_data['results'][0]

            for x in range(0, len(results)):
                pvp_match = results[x]

                # Checks if the last played SR match has a higher Unix Value than the last played other Match (Turf, Ranked, League, Private)
                # If yes, insert the data of the last played Salmon Run Match in the results
                if pvp_match['start_time'] < coop_match['start_time']:
                    results.insert(x, coop_match)
                    break
        
        return results

