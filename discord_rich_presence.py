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
timeout_minutes = 300000
show_weapon = True  # change to False to remove weapon name from discord details


def get_minutes_since():
    
    matches = nso.load_results()

    # When Previous Match was Salmon Run
    if matches[0].get('job_result') is not None:
        match_end = int(
            matches[0]["play_time"])

    # When Previous Match was Turf, Ranked, League or Private
    else:
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
    logger.info("Check discord!")

    # Get friend code from config, and add config option if does not exist
    try:
        friend_code = config['friend_code']
    except KeyError:
        config['friend_code'] = 'Unset'
        config_f = open("config.txt", "w")
        config_f.write(json.dumps(config, sort_keys=True, indent=4, ))
        config_f.close()
        friend_code = config['friend_code']

    while True:  # The presence will stay on as long as the program is running

        for i in range(0, 5):
            minutes_since, last_match = get_minutes_since()

            # int is here so we don't have funky floating point madness
            seconds_since = int(minutes_since * 60)
            hours_since = int(minutes_since / 60)
            
            # When Previous Match was Salmon Run
            # job_result is only present in salmon run JSON
            if last_match.get('job_result') is not None:

                # Sets Gamemode Key in order to change the Picture
                gamemode_key = "salmon_run"

                # Decides if last Run is shown in hours, minutes or seconds
                if minutes_since >= 60:
                    details = "Last Run: {} h(s) ago".format(hours_since)
                elif minutes_since > 1:
                    details = "Last Run: {} min(s) ago".format(
                        math.floor(minutes_since)
                    )
                else:
                    details = "Last Run: {} sec(s) ago".format(
                        seconds_since
                    )

                # Deciding the Result
                if last_match['job_result']['is_clear']:
                    outcome = "WON"
                else:
                    outcome = "LOST"

                ### Checks how many waves were played on last Run
                # If all 3 Waves were played
                if last_match["wave_details"][2]:
                    goldEgg = last_match["wave_details"][0]["golden_ikura_num"] + \
                        last_match["wave_details"][1]["golden_ikura_num"] + \
                        last_match["wave_details"][2]["golden_ikura_num"]
                    powEgg = last_match["wave_details"][0]["ikura_num"] + \
                        last_match["wave_details"][1]["ikura_num"] + \
                        last_match["wave_details"][2]["ikura_num"]

                # If only 2 Waves were played
                elif not last_match["wave_details"][2] and last_match["wave_details"][1]:
                    goldEgg = last_match["wave_details"][0]["golden_ikura_num"] + last_match["wave_details"][1]["golden_ikura_num"]
                    powEgg = last_match["wave_details"][0]["ikura_num"] + last_match["wave_details"][1]["ikura_num"]

                # If only 1 Wave was played
                else:
                    goldEgg = last_match["wave_details"][0]["golden_ikura_num"]
                    powEgg = last_match["wave_details"][0]["ikura_num"]

                # When hovering on the Picture
                large_text = "Last match was Salmon Run on {}".format(
                    last_match['schedule']['stage']['name'] 
                )

                # IGN and Salmon Run Rank
                if i == 0:
                    details = "IGN: {}".format(
                        last_match["my_result"]["name"]
                    )
                    state = "{} {}".format(
                        (last_match["grade"])["long_name"],
                        last_match["grade_point"]
                    )

                # Friend code
                elif i == 1:
                    if not friend_code:
                        state = "FC: Not Given"
                    else:
                        state = "FC: {}".format(friend_code)

                # Hazard Level
                elif i == 2:
                    state = "Hazard Level: {}".format(
                        str(last_match["danger_rate"]) + "%"
                    )

                # Result and Total Collected Golden Eggs / Power Eggs
                elif i == 3:
                   details = "{}".format(
                       outcome
                   )

                   state = "{} GoldEggs / {} powEggs".format(
                       goldEgg,
                       powEgg
                   )

                # Save / Death Ratio
                elif i == 4:
                    state = "Save/Death Ratio: {}/{}".format(
                        last_match["my_result"]["help_count"],
                        last_match["my_result"]["dead_count"]
                    )

                if minutes_since < timeout_minutes:
                    RPC.update(
                        details=details,
                        state=state, 
                        large_image=gamemode_key, 
                        small_image="default",
                        large_text=large_text
                    )
                else:
                    RPC.clear()
                    logger.debug("RPC cleared, not in game long enough")
                time.sleep(time_interval)

            # When Previous Match was Turf, Ranked, League or Private
            else:

                # Decides if last Match is shown in hours, minutes or seconds
                if minutes_since >= 60:
                    details = "Last match: {} h(s) ago".format(hours_since)
                elif minutes_since > 1:
                    details = "Last match: {} min(s) ago".format(
                        math.floor(minutes_since))
                else:
                    details = "Last match: {} sec(s) ago".format(seconds_since)

                # When hovering on the Picture
                large_text = "Last match was {}, {} on {}".format(
                    last_match["game_mode"]["name"], 
                    last_match["rule"]["name"], 
                    last_match["stage"]["name"]
                )

                # Gets Gamemode Key in order to change the Picture
                gamemode_key = last_match["rule"]["key"]

                # IGN and Level
                if i == 0:
                    details = "IGN: {}".format(
                        last_match["player_result"]["player"]["nickname"]
                    )

                    if not last_match["star_rank"]:
                        state = "Level: {}".format(
                            last_match["player_result"]["player"]["player_rank"]
                        )
                    else:
                        state = "Level: {}☆{}".format(
                            last_match["player_result"]["player"]["player_rank"],
                            last_match["player_result"]["player"]["star_rank"]
                        )

                # Friend Code
                elif i == 1:
                    if not friend_code:
                        state = "FC: Not Given"
                    else:
                        state = "FC: {}".format(friend_code)

                # Kill (Assist) / Death Ratio
                elif i == 2:
                    state = "K(A)/D: {}({})/{}".format(
                        last_match["player_result"]["kill_count"],
                        last_match["player_result"]["assist_count"],
                        last_match["player_result"]["death_count"]
                    )

                # Result and Percentages
                elif i == 3:
                    details = last_match["my_team_result"]["name"]
                    try:
                        state = "{}% vs {}%".format(
                            last_match["my_team_percentage"], last_match["other_team_percentage"]
                        )
                    except KeyError:
                        try:
                            state = "{} vs {}".format(
                                last_match["my_team_count"], last_match["other_team_count"]
                            )
                        except KeyError:
                            state = "Gamemode not yet supported"

                # Used Weapon and Total Points
                elif i == 4:
                    state = "{}p".format(
                        last_match["player_result"]["game_paint_point"]
                    )

                    if show_weapon:
                        details = "{}".format(
                            last_match["player_result"]["player"]["weapon"]["name"]
                        )
                    else:
                        pass
                   
                if minutes_since < timeout_minutes:
                    RPC.update(
                        details=details,
                        state=state,
                        large_image=gamemode_key,
                        small_image="default",
                        large_text=large_text
                    )
                else:
                    RPC.clear()
                    logger.debug("RPC cleared, not in game long enough")
                time.sleep(time_interval)


if __name__ == "__main__":
    main()
