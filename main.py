import interactions
import requests
import discord
import sqlite3
import asyncio
import os
import logging
from variables import discord_token
from configparser import ConfigParser
import time


logging.basicConfig(filename='logs\debug-'+str(time.time())+'.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#file reading
def readGlobalVariable(name: str) :
    config = ConfigParser()
    path_to_config = os.path.dirname(__file__)+"\config.cfg"
    config.read(path_to_config)

    return config["Global Variables"][name]

def writeGlobalVariable(name: str, value : str) : 
    config = ConfigParser()
    path_to_config = os.path.dirname(__file__)+"\config.cfg"
    config.read(path_to_config)
    
    config["Global Variables"][name] = value
    with open(path_to_config, 'w') as conf:
        config.write(conf)

def internalSoftReset():    
    writeGlobalVariable("index","0")
    writeGlobalVariable("count","0")

bot = interactions.Client(discord_token)

#discord events
@bot.event
async def on_ready():
    logging.info("starting updates")
    while(True):
        if os.path.isfile(os.path.dirname(__file__)+"\database.db"):
            users = fetchUsersFromDB()
            writeGlobalVariable("count",str(users.__len__()))
            #await asyncio.sleep(60)
            count = users.__len__()
            while(int(readGlobalVariable("count")) == count):
                index = int(readGlobalVariable("index"))
                count = int(readGlobalVariable("count"))
                if not (index > count):
                    updateUsers(index, users)
                else : 
                    pass    
                await asyncio.sleep(150)
        else:
            logging.info("Database does not exist yet waiting...")
            await asyncio.sleep(60)
        
    

#discord methods
def fetchDataForUser(region,name,tag):
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{name}/{tag}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise ValueError(data["error"])
        
        return data
        
    except requests.exceptions.RequestException as e:
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        raise ValueError(str(e))

def save_data(data : requests.Response.json, discord_id: int, region: str):
    
    player_name = data["data"]["name"]
    player_tag = data["data"]["tag"]
    player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    player_puuid = data["data"]["puuid"]
    
    connection = initDatabase("database.db")
    db = connection.cursor()
    initTable(db)
    
    db.execute("SELECT * FROM valorant_players WHERE player_puuid=?", (player_puuid,))
    data = db.fetchone()
    if data:
        if data[4]!=discord_id:
            logging.info("User is already registered under another discord id, try again.")
            deinitDatabase(connection)
            return
    
    db.execute("SELECT * FROM valorant_players WHERE discord_id=? AND player_puuid=?", (discord_id, player_puuid,))
    data = db.fetchone()
    if data: 
        if data[4]==discord_id:
            logging.info("updating for existing discord user")
            db.execute("UPDATE valorant_players SET player_cur_rank=? WHERE discord_id=? AND player_puuid=?", (player_cur_rank, discord_id, player_puuid,))
        else :
            logging.info("inserting non-existing discord user")
            db.execute("INSERT INTO valorant_players (player_region, player_name, player_tag, player_cur_rank, player_puuid, discord_id) VALUES (?,?,?,?,?,?)", (region, player_name, player_tag, player_cur_rank, player_puuid, discord_id,))
    else:
        logging.info("inserting non-existing discord user because data null")
        db.execute("INSERT INTO valorant_players (player_region, player_name, player_tag, player_cur_rank, player_puuid, discord_id) VALUES (?,?,?,?,?,?)", (region, player_name, player_tag, player_cur_rank, player_puuid, discord_id,))
        
    saveDatabaseChanges(connection)
    deinitDatabase(connection)


def fetchUsersFromDB():
    connection = initDatabase("database.db")
    db = connection.cursor()
    
    db.execute("SELECT * FROM valorant_players ORDER BY discord_id")
    data_list=db.fetchall()
    saveDatabaseChanges(connection)
    deinitDatabase(connection)
    return data_list
    
def updateUsers(index : int, users : list(tuple())):
    #0region #1name #2tag #3rank #4puuid #5discord_id
    logging.info("running update users")
    for i in range(5): 
        user = users[int(readGlobalVariable("index"))]
        logging.info("fetching data for user in region " + str(user[0]) + ", name and tag as " + str(user[1]) +" #"+ str(user[2]))
        data = fetchDataForUser(user[0], user[1], user[2])
        #logging.info("data "+ str(data))
        updateRank(data["data"]["current_data"]["currenttierpatched"], user[5], user[4])
        
        count = int(readGlobalVariable("count"))
        i = int(readGlobalVariable("index"))
        if i == count-1 :
            writeGlobalVariable("index", str(0))
        else : 
            writeGlobalVariable("index", str(i + 1))
        logging.info("going to next user")

def updateRank(player_cur_rank, discord_id, player_puuid):
    connection = initDatabase("database.db")
    db = connection.cursor()
    db.execute("UPDATE valorant_players SET player_cur_rank=? WHERE discord_id=? AND player_puuid=?", (player_cur_rank, discord_id, player_puuid,))
    saveDatabaseChanges(connection)
    deinitDatabase(connection)
    
#database functions
def initDatabase(address : str):
    connection = sqlite3.connect(address)
    return connection

def saveDatabaseChanges(connection : sqlite3.Connection):
    connection.commit()
    
def deinitDatabase(connection : sqlite3.Connection):
    connection.close()
    
def initTable(connection : sqlite3.Cursor):
    connection.execute('''CREATE TABLE IF NOT EXISTS valorant_players (player_region TEXT, player_name TEXT, player_tag TEXT, player_cur_rank TEXT, player_puuid INTEGER, discord_id INTEGER)''')

#bot commands
@bot.command(
    name="add_valorant_account",
    description="Auto Valorant account rank role adder.",
    options = [
        interactions.Option(
            name="region",  
            description="Example NA",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="name",
            description="Example nhmln",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="tag",
            description="Example NA1",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)

#discord command methods
async def adder_command(ctx: interactions.CommandContext,region: str, name: str, tag: str):
    try:
        #player_name, player_tag, player_cur_rank, player_elo, player_high_rank = fetchDataForUser(region, name, tag)
        
        data = fetchDataForUser(region, name, tag)
        
        player_name = data["data"]["name"]
        player_tag = data["data"]["tag"]
        player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
        discord_id = int(ctx.author.id)
        save_data(data, discord_id, region)
        
        if player_cur_rank == None :
            rank_name = "Unranked"
            player_cur_rank = "Unranked"
        else:
            rank_name = ' '.join(player_cur_rank.split()[:-1])
            
        await ctx.send(f"Player {player_name} #{player_tag}'s role has been updated to {player_cur_rank}.")

        ranks = {
            "Iron": discord.Colour.from_rgb(139, 94, 60),
            "Bronze": discord.Colour.from_rgb(205, 127, 50),
            "Silver": discord.Colour.from_rgb(192, 192, 192),
            "Gold": discord.Colour.from_rgb(255, 215, 0),
            "Platinum": discord.Colour.from_rgb(229, 228, 226),
            "Diamond": discord.Colour.from_rgb(185, 242, 255),
            "Immortal": discord.Colour.from_rgb(100, 65, 165),
            "Radiant": discord.Colour.from_rgb(245, 166, 35),
            "Unranked": discord.Colour.default()
        }
            
        if rank_name in ranks:
            color = ranks[rank_name].value
            role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
            if role is None:
                await ctx.guild.create_role(name="Valorant | "+player_cur_rank, color=color)
            role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
            await ctx.author.add_role(role)

    except ValueError as e:
        await ctx.send(str(e))

internalSoftReset()
bot.start()