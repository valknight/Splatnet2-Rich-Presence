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

    # Date + Time Now
    time_now = datetime.utcnow()

    # Date + Time from last played match/run (Unix Timestamp to DateTime)
    time_match = datetime.utcfromtimestamp(match_end)

    # Calculate time difference between the two dates
    time_to_last_match = time_now - time_match

    # Get minutes since last Match/Run
    minutes_since = time_to_last_match.total_seconds() / 60
    return minutes_since, matches[0]

#Return "s" if there needs to be plural, else it doesn't
def plural_logic(nbr):
    return "" if nbr == 1 else "s"

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

            # Calculating the secs/hours/days since Last Match/Run
            seconds_since   = int(minutes_since * 60)
            hours_since     = int(minutes_since / 60)
            days_since      = int(minutes_since / 1440)
            
            # When Previous Match was Salmon Run
            # job_result is only present in salmon run JSON
            if last_match.get('job_result') is not None:

                # Sets Gamemode Key in order to change the Picture
                gamemode_key = "salmon_run"

                # Decides if last Run is shown in days, hours, minutes or seconds
                # In Days
                if minutes_since >= 1440:
                    details = "Last Run: {} day{} ago".format(days_since, plural_logic(days_since))

                # In Hours
                elif minutes_since >= 60:
                    details = "Last Run: {} h{} ago".format(hours_since, plural_logic(hours_since))
                
                # In Minutes
                elif minutes_since > 1:
                    details = "Last Run: {} min{} ago".format(math.floor(minutes_since), plural_logic(math.floor(minutes_since)))
                
                # In Seconds
                else:
                    details = "Last Run: {} sec{} ago".format(seconds_since, plural_logic(seconds_since))


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
                   details = "GoldEgg/PowEgg ({})".format(
                       outcome
                   )

                   state = "{} / {}".format(
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

                # Decides if last Match is shown in days, hours, minutes or seconds
                # In Days
                if minutes_since >= 1440:
                    details = "Last Match: {} day{} ago".format(days_since, plural_logic(days_since))

                # In Hours
                elif minutes_since >= 60:
                    details = "Last Match: {} h{} ago".format(hours_since, plural_logic(hours_since))

                # In Minutes
                elif minutes_since > 1:
                    details = "Last Match: {} min{} ago".format(math.floor(minutes_since), plural_logic(math.floor(minutes_since)))

                # In Seconds
                else:
                    details = "Last Match: {} sec{} ago".format(seconds_since, plural_logic(seconds_since))


                # When hovering on the Picture
                large_text = "Last match was {}, {} on {}".format(
                    last_match["game_mode"]["name"], 
                    last_match["rule"]["name"], 
                    last_match["stage"]["name"]
                )

                # Gets Gamemode Key in order to change the Picture
                gamemode_key = last_match["rule"]["key"]

                # Gets Lobby Key
                lobby_key = last_match["game_mode"]["key"]

                # IGN and Level (+ Rank)
                if i == 0:
                    details = "IGN: {}".format(
                        last_match["player_result"]["player"]["nickname"]
                    )

                    # Checks if player has a Level Star
                    # If player has no Level Star (yet XP)
                    if not last_match["star_rank"]:

                        # If last match was in a Regular Lobby (Turf War) or Private Lobby
                        if lobby_key == "regular" or lobby_key == "private":
                            state = "Level: {}".format(
                                last_match["player_result"]["player"]["player_rank"],
                            )

                        # If last match was in a Ranked Solo Lobby
                        elif lobby_key == "gachi":

                            # If last match was Splat Zones
                            if gamemode_key == "splat_zones":
                                
                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}/R(SZ): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}/R(SZ): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}/R(SZ): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}/R(SZ): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"]
                                    )

                            # If last match was Tower Control
                            elif gamemode_key == "tower_control":

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}/R(TC): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}/R(TC): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}/R(TC): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}/R(TC): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"]
                                    )

                            # If last match was Rainmaker
                            elif gamemode_key == "rainmaker":

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}/R(RM): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}/R(RM): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}/R(RM): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}/R(RM): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"]
                                    )

                            # If last match was Clam Blitz
                            else: 

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}/R(CB): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}/R(CB): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}/R(CB): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}/R(CB): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["udemae"]["name"]
                                    )
                        
                        # If last match was in a League Pair/Team Lobby
                        elif lobby_key == "league_pair" or lobby_key == "league_team":

                            # Checks if Player has League Power
                            # If Player has no League Power (yet XP)
                            if not last_match["league_point"]:
                                state = "Lvl: {}/Power: TBD".format(
                                    last_match["player_result"]["player"]["player_rank"]
                                )
                            
                            # If Player has League Power
                            else:
                               state = "Lvl: {}/Power: {}".format(
                                   last_match["player_result"]["player"]["player_rank"],
                                   last_match["league_point"]
                               )

                    # If player has a Level Star
                    else:

                        # If last match was in a Regular Lobby (Turf War) or Private Lobby
                        if lobby_key == "regular" or lobby_key == "private":
                            state = "Level: {}☆{}".format(
                                last_match["player_result"]["player"]["player_rank"],
                                last_match["player_result"]["player"]["star_rank"],
                            )

                        # If last match was in a Ranked Solo Lobby
                        elif lobby_key == "gachi":

                            # If last match was Splat Zones
                            if gamemode_key == "splat_zones":

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}☆{}/R(SZ): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}☆{}/R(SZ): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}☆{}/R(SZ): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}☆{}/R(SZ): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"]
                                    )

                            # If last match was Tower Control
                            elif gamemode_key == "tower_control":

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}☆{}/R(TC): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}☆{}/R(TC): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}☆{}/R(TC): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}☆{}/R(TC): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"]
                                    )


                            # If last match was Rainmaker
                            elif gamemode_key == "rainmaker":
                                
                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}☆{}/R(RM): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )

                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}☆{}/R(RM): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                        )

                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}☆{}/R(RM): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                            last_match["x_power"]
                                        )

                                # If player has other Ranks
                                else:
                                    state = "Lvl: {}☆{}/R(RM): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"]
                                    )

                            # If last match was Clam Blitz
                            elif gamemode_key == "clam_blitz":

                                # If player has S+ Rank
                                if last_match["udemae"]["name"] == "S+":
                                    state = "Lvl: {}☆{}/R(CZ): {}{}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"],
                                        last_match["udemae"]["s_plus_number"]
                                    )
                                
                                # If player has X Rank
                                elif last_match["udemae"]["name"] == "X":

                                    # Checks if Player has any X Power
                                    # If Player has no X Power (yet XP)
                                    if not last_match["x_power"]:
                                        state = "Lvl: {}☆{}/R(CZ): X(TBD)".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                        )
                                        
                                    # If Player has X Power
                                    else:
                                        state = "Lvl: {}☆{}/R(CZ): X({})".format(
                                            last_match["player_result"]["player"]["player_rank"],
                                            last_match["player_result"]["player"]["star_rank"],
                                            last_match["x_power"]
                                        )
                                
                                # If player has other Ranks
                                else: 
                                    state = "Lvl: {}☆{}/R(CZ): {}".format(
                                        last_match["player_result"]["player"]["player_rank"],
                                        last_match["player_result"]["player"]["star_rank"],
                                        last_match["udemae"]["name"]
                                    )

                        # If last match was in a League Pair/Team Lobby
                        elif lobby_key == "league_pair" or lobby_key == "league_team":
                            
                            # Checks if Player has League Power
                            # If Player has no League Power (yet XP)
                            if not last_match["league_point"]:
                                state = "Lvl: {}☆{}/Power: TBD".format(
                                    last_match["player_result"]["player"]["player_rank"],
                                    last_match["player_result"]["player"]["star_rank"],
                                )

                            # If Player has League Power
                            else:
                               state = "Lvl: {}☆{}/Power: {}".format(
                                   last_match["player_result"]["player"]["player_rank"],
                                   last_match["player_result"]["player"]["star_rank"],
                                   last_match["league_point"]
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
