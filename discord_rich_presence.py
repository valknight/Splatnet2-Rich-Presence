import json
import math
import os
import time
import pypresence
import click
import nso_functions

from pypresence import Presence
from datetime import datetime, timedelta
from config.logger import logger

# this acts as the core controller which allows us to interface with the Splatnet API
nso = nso_functions.NSOInterface()

# config
client_id = '488433036665552897'  # client id for discord rich presence
# this is the interval at which your rich presence updates. default is 3 seconds
time_interval = 3
# time it takes for the bot to declare you not playing splatoon in minutes
timeout_minutes = 30
show_weapon = True  # change to False to remove weapon name from discord details


def get_minutes_since():
    matches = nso.load_results()
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
    minutes_since = time_to_last_match.hour * 60 + \
        time_to_last_match.minute + time_to_last_match.second / 60
    return minutes_since, matches[0]


@click.command()
def main():
    logger.info("Checking for updates...")
    os.system("git pull")
    logger.info(
        "If updates were done, restart this script by using CTRL-C to terminate it, and re run it.")

    # Make connection to Discord
    try:
        RPC = Presence(client_id)  # Initialize the Presence class
        RPC.connect()  # Start the handshake loop
    except pypresence.exceptions.InvalidPipe:
        logger.error(
            "Could not connect to the discord pipe. Please ensure it's running.")
        exit(1)
    except FileNotFoundError:
        logger.error(
            "Could not connect to the discord pipe. Please ensure it's running.")
        exit(1)

    # Load our current config

    config = nso_functions.get_config_file()

    logger.info("Logged into Splatnet2")

    # get friend code from config, and add config option if does not exist
    try:
        friend_code = config['friend_code']
    except KeyError:
        config['friend_code'] = 'Unset'
        config_f = open("config.txt", "w")
        config_f.write(json.dumps(config, sort_keys=True, indent=4, ))
        config_f.close()
        friend_code = config['friend_code']

    while True:  # The presence will stay on as long as the program is running

        for i in range(0, 4):
            minutes_since, last_match = get_minutes_since()
            # int is here so we don't have funky floating point madness
            seconds_since = int(minutes_since * 60)
            hours_since = int(minutes_since / 60)
            if minutes_since >= 60:
                details = "Last match: {} hour(s) ago".format(hours_since)
            elif minutes_since > 1:
                details = "Last match: {} minute(s) ago".format(
                    math.floor(minutes_since))
            else:
                details = "Last match: {} second(s) ago".format(seconds_since)
            # job_result is only present in salmon run JSON
            if last_match.get('job_result') is not None:
                gamemode_key = "salmon_run"
                if last_match['job_result']['is_clear']:
                    outcome = "losing"
                else:
                    outcome = "winning"
                large_text = "Last match was Salmon Run, {} with {} eggs".format(
                    outcome, last_match['job_score'])
                if i == 0:
                    state = "Grade: {}".format(
                        (last_match["grade"])["long_name"])
                elif i == 1:
                    state = "Friend code: {}".format(friend_code)
                elif i == 2:
                    state = "Difficulty: {}".format(
                        str(last_match["danger_rate"]))
                elif i == 3:
                    state = "Played on {}".format(
                        last_match['schedule']['stage']['name'])
            else:
                large_text = "Last match was {}, {} on {}".format(
                    last_match["game_mode"]["name"], last_match["rule"]["name"], last_match["stage"]["name"])
                gamemode_key = last_match["rule"]["key"]
                if i == 0:
                    state = "Friend code: {}".format(friend_code)
                elif i == 1:
                    state = "K/D: {}/{}".format(last_match["player_result"]["kill_count"],
                                                last_match["player_result"]["death_count"])
                elif i == 2:
                    details = last_match["my_team_result"]["name"]
                    try:
                        state = "{}% vs {}%".format(
                            last_match["my_team_percentage"], last_match["other_team_percentage"])
                    except KeyError:
                        try:
                            state = "{} vs {}".format(
                                last_match["my_team_count"], last_match["other_team_count"])
                        except KeyError:
                            state = "Gamemode not yet supported"

                elif i == 3:
                    state = "{}p".format(
                        last_match["player_result"]["game_paint_point"])
                    if show_weapon:
                        details = "{}".format(
                            last_match["player_result"]["player"]["weapon"]["name"])
                    else:
                        pass
            if minutes_since < timeout_minutes:
                RPC.update(details=details, state=state, large_image=gamemode_key, small_image="default",
                           large_text=large_text)
            else:
                RPC.clear()
                logger.debug("RPC cleared, not in game long enough")
            time.sleep(time_interval)


if __name__ == "__main__":
    main()
