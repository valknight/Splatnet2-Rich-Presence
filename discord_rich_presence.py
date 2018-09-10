import json
import math
import os
import time
from datetime import datetime, timedelta

import pypresence
from pypresence import Presence

try:
    from splatnet2statink import load_results
except ModuleNotFoundError:
    print("Could not find splatnet2statink installed. Please run the installation script first.")
    exit(1)

# config
client_id = '488433036665552897'  # client id for discord rich presence
time_interval = 3  # this is the interval at which your rich presence updates. default is 3 seconds
timeout_minutes = 30  # time it takes for the bot to declare you not playing splatoon in minutes


def get_minutes_since():
    matches = load_results()
    a = open("matches.json", "w")
    a.write(json.dumps(matches))
    a.close()
    last_match = open("last_match.json", "w")
    last_match.write(json.dumps(matches[0]))
    last_match.close()
    try:
        match_end = int(matches[0]["start_time"] + matches[0][
            "elapsed_time"])  # adds the seconds of the match to the unix time of the match starting
    except KeyError:
        match_end = int(matches[0][
                            "start_time"] + 180)  # we assume that the match lasted 3 minutes here, as sometimes the API doesn't give us how long the match took
    match_end_time = timedelta(0, match_end)
    match_time_diff = datetime.utcnow()
    time_to_last_match = match_time_diff - match_end_time
    # get minutes since last match
    minutes_since = time_to_last_match.hour * 60 + time_to_last_match.minute + time_to_last_match.second / 60
    return minutes_since


if __name__ == "__main__":
    print("Checking for updates...")
    os.system("git pull")
    print("If updates were done, restart this script by using CTRL-C to terminate it, and re run it.")
    try:
        RPC = Presence(client_id)  # Initialize the Presence class
        RPC.connect()  # Start the handshake loop
    except pypresence.exceptions.InvalidPipe:
        print("Could not connect to the discord pipe. Please ensure it's running.")

    get_minutes_since()  # we run this once to ensure the login flow is complete
    print("\n\nLogged into Splatnet2\n\n")
    print("IF NO IMAGE LOADS\nI am currently unsure of all the gamemode keys the API returns. \nIf you don't see an "
          "iamge in discord, "
          "make an issue on Github, and include the game mode you played, as well your \"last_match.json\" file, "
          "to assist in debugging. Thanks!")
    config_f = open("config.txt", "r")
    config = json.loads(config_f.read())
    config_f.close()

    # get friend code from config, and add config option if does not exist
    try:
        friend_code = config['friend_code']
    except KeyError:
        config['friend_code'] = 'Unset'
        config_f = open("config.txt", "w")
        config_f.write(json.dumps(config, sort_keys = True, indent = 4, ))
        config_f.close()
        friend_code = config['friend_code']

    while True:  # The presence will stay on as long as the program is running

        for i in range(0, 4):
            minutes_since = get_minutes_since()
            last_match_f = open("last_match.json", "r")
            last_match = json.loads(last_match_f.read())
            last_match_f.close()
            seconds_since = int(minutes_since * 60)  # int is here so we don't have funky floating point madness
            hours_since = int(minutes_since / 60)
            if minutes_since >= 60:
                details = "Last match: {} hour(s) ago".format(hours_since)
            elif minutes_since > 1:
                details = "Last match: {} minute(s) ago".format(math.floor(minutes_since))
            else:
                details = "Last match: {} second(s) ago".format(seconds_since)
            if i == 0:
                state = "Friend code: {}".format(friend_code)
            elif i == 1:
                state = "K/D: {}/{}".format(last_match["player_result"]["kill_count"],
                                            last_match["player_result"]["death_count"])
            elif i == 2:
                details = last_match["my_team_result"]["name"]
                try:
                    state = "{}% vs {}%".format(last_match["my_team_percentage"], last_match["other_team_percentage"])
                except KeyError:
                    try:
                        state = "{} vs {}".format(last_match["my_team_count"], last_match["other_team_count"])
                    except KeyError:
                        state = "Gamemode not yet supported"

            elif i == 3:
                state = "{}p".format(last_match["player_result"]["game_paint_point"])
            if minutes_since < timeout_minutes:
                RPC.update(details = details, state = state, large_image = last_match["rule"]["key"], small_image =
                "default",
                           large_text = "Last match was {}, {} on {}".format(last_match["game_mode"]["name"],
                                                                             last_match["rule"]["name"], last_match[
                                                                                 "stage"]["name"]))
            else:
                RPC.clear()
                print("{} : RPC cleared, not in game long enough".format(datetime.now()))
            time.sleep(time_interval)
