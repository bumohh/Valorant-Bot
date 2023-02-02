#External
import requests
import sqlite3
#Internal
import log

# Function that calls the api and returns rank and puuid
def InitialValApiCall(region, ign, tag):
    log.debug("InitialValApiCall in slash_functions.py triggered.")
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{ign}/{tag}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            log.debug("InitialValApiCall in slash_functions.py finished incorrectly first error.")
            raise ValueError(data["error"])
        log.debug("InitialValApiCall in slash_functions.py finished correctly.")
        return data["data"]["current_data"]["currenttierpatched"],data["data"]["puuid"],data["data"]["current_data"]["images"]["large"]
          
    except requests.exceptions.RequestException as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly second error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("InitialValApiCall in slash_functions.py finished incorrectly third error.")
        raise ValueError(str(e))

def bannerValApiCall(ign, tag):
    
    log.debug("bannerValApiCall in slash_functions.py triggered.")
    endpoint = f"https://api.henrikdev.xyz/valorant/v1/account/{ign}/{tag}?force=true"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            log.debug("bannerValApiCall in slash_functions.py finished incorrectly first error.")
            raise ValueError(data["error"])
        log.debug("bannerValApiCall in slash_functions.py finished correctly.")
        return data["data"]["card"]["wide"]
          
    except requests.exceptions.RequestException as e:
        log.debug("bannerValApiCall in slash_functions.py finished incorrectly second error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("bannerValApiCall in slash_functions.py finished incorrectly third error.")
        raise ValueError(str(e))


# Function to check if account has already been added to the user
def duplicateCheck(puuid):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players WHERE puuid=?", (puuid,))
    rows = cursor.fetchall()
    cursor.close()
    connect.close()

    if len(rows) == 0:
        return False
    else:
        return True

# Function to make the first save to the database initiated from the slash command    
def initialDatabaseSave(discord_id, region, ign, tag, rank_full, puuid):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players WHERE discord_id=? AND puuid=?", (discord_id, puuid,))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE valorant_players SET region=?, ign=?, tag=?, rank_full=? WHERE discord_id=? AND puuid=?", (region, ign, tag, rank_full, discord_id, puuid,))
    else:
        cursor.execute("""INSERT INTO valorant_players (discord_id, region, ign, tag, rank_full, puuid)VALUES (?,?,?,?,?,?)""", (discord_id, region, ign, tag, rank_full, puuid))
    connect.commit()
    cursor.close()
    connect.close()

def removeValorantAccountfromDatabase(discord_id):
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("DELETE FROM valorant_players WHERE discord_id=?", (discord_id,))
    connect.commit()
    cursor.close()
    connect.close()



