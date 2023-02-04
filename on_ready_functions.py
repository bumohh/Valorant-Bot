#External
import requests
import sqlite3
#Internal
import log


# Function to initiate the basic database
def initDatabase():
    log.debug("initDatabase in on_ready_functions.py triggered.")
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS valorant_players (discord_id TEXT, region TEXT, ign TEXT, tag TEXT, rank_full TEXT, puuid TEXT, verification_status TEXT)""")
    connect.commit()
    cursor.close()
    connect.close()
    log.debug("initDatabase in on_ready_functions.py finished.")

# Function to see if database is empty
def isDatabaseEmpty():
    log.debug("isDatabaseEmpty in on_ready_functions.py triggered.")
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players")
    rows = cursor.fetchall()
    cursor.close()
    connect.close()

    if len(rows) == 0:
        log.debug("isDatabaseEmpty in on_ready_functions.py finshed and returned True.")
        return True
    else:
        log.debug("isDatabaseEmpty in on_ready_functions.py finshed and returned False.")
        return False

# Function to read resources from database
def readDatabase():
    log.debug("readDatabase in on_ready_functions.py triggered.")
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM valorant_players ORDER BY discord_id")
    database_list = cursor.fetchall()
    cursor.close()
    connect.close()
    log.debug("readDatabase in on_ready_functions.py finished.")
    return database_list

# Function collect data from api based on puuid
def regularValApiCall(region,puuid):
    log.debug("regularValApiCall in on_ready_functions.py triggered.")
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{puuid}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise ValueError(data["error"])
        
        rank    =   data["data"]["current_data"]["currenttierpatched"]
        ign     =   data["data"]["name"]
        tag     =   data["data"]["tag"]
        
        log.debug("regularValApiCall in on_ready_functions.py finished correctly.")
        return rank, ign, tag
        
    except requests.exceptions.RequestException as e:
        log.debug("regularValApiCall in on_ready_functions.py finished incorrectly first error.")
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        log.debug("regularValApiCall in on_ready_functions.py finished incorrectly second error.")
        raise ValueError(str(e))
    

# Function to update database
def updateDatabase(rank_full, ign, tag, discord_id, puuid):
    log.debug("updateDatabase in on_ready_functions.py triggered.")
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()
    cursor.execute("UPDATE valorant_players SET rank_full=?, ign=?, tag=? WHERE discord_id=? AND puuid=?", (rank_full, ign, tag, discord_id, puuid))
    connect.commit()
    cursor.close()
    connect.close()
    log.debug("updateDatabase in on_ready_functions.py finished")


