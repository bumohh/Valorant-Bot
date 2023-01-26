import interactions
import requests
import discord
import sqlite3
from token import _token

bot = interactions.Client(token=_token)

def fetchDataForUser(region,name,tag):
    endpoint = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{name}/{tag}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            raise ValueError(data["error"])
        
        save_data(data)
        
    except requests.exceptions.RequestException as e:
        raise ValueError("Error connecting to API: " + str(e))
    except ValueError as e:
        raise ValueError(str(e))

def save_data(data : requests.Response.json):
    
    player_name = data["data"]["name"]
    player_tag = data["data"]["tag"]
    player_cur_rank = data["data"]["current_data"]["currenttierpatched"]
    player_puuid = data["data"]["puuid"]
    discord_id = 3261
    
    connection = initDatabase("database.db")
    db = connection.cursor()
    initTable(db)
    
    db.execute("SELECT * FROM valorant_players WHERE player_puuid=?", (player_puuid,))
    data = db.fetchone()
    if data:
        if data[4]!=discord_id:
            print("User is already registered under another discord id, try again.")
            deinitDatabase(connection)
            return
    
    db.execute("SELECT * FROM valorant_players WHERE discord_id=? AND player_puuid=?", (discord_id, player_puuid,))
    data = db.fetchone()
    if data: 
        if data[4]==discord_id:
            print("updating for existing discord user")
            db.execute("UPDATE valorant_players SET player_cur_rank=? WHERE discord_id=? AND player_puuid=?", (player_cur_rank, discord_id, player_puuid,))
        else :
            print("inserting non-existing discord user")
            db.execute("INSERT INTO valorant_players (player_name, player_tag, player_cur_rank, player_puuid, discord_id) VALUES (?,?,?,?,?)", (player_name, player_tag, player_cur_rank, player_puuid, discord_id,))
    else:
        print("inserting non-existing discord user because data null")
        db.execute("INSERT INTO valorant_players (player_name, player_tag, player_cur_rank, player_puuid, discord_id) VALUES (?,?,?,?,?)", (player_name, player_tag, player_cur_rank, player_puuid, discord_id,))
        
    saveDatabaseChanges(connection)
    deinitDatabase(connection)


def initTable(connection : sqlite3.Cursor):
    connection.execute('''CREATE TABLE IF NOT EXISTS valorant_players (player_name TEXT, player_tag TEXT, player_cur_rank TEXT, player_puuid, discord_id INTEGER)''')


#database functions
def initDatabase(address : str):
    connection = sqlite3.connect(address)
    return connection

def saveDatabaseChanges(connection : sqlite3.Connection):
    connection.commit()
    
def deinitDatabase(connection : sqlite3.Connection):
    connection.close()


#discord commands
async def adder_command(region: str, name: str, tag: str):
    try:
        player_name, player_tag, player_cur_rank = fetchDataForUser(region, name, tag)
        #discord_username = ctx.author.name
        save_data(player_name, player_tag, player_cur_rank)
        #await ctx.send(f"Player {player_name} #{player_tag}'s role has been updated to {player_cur_rank}.")

        ranks = {
            "Iron": discord.Colour.from_rgb(139, 94, 60),
            "Bronze": discord.Colour.from_rgb(205, 127, 50),
            "Silver": discord.Colour.from_rgb(192, 192, 192),
            "Gold": discord.Colour.from_rgb(255, 215, 0),
            "Platinum": discord.Colour.from_rgb(229, 228, 226),
            "Diamond": discord.Colour.from_rgb(185, 242, 255),
            "Immortal": discord.Colour.from_rgb(100, 65, 165),
            "Radiant": discord.Colour.from_rgb(245, 166, 35)
        }
        rank_name = ' '.join(player_cur_rank.split()[:-1])
        #if rank_name in ranks:
            #color = ranks[rank_name].value
            #role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
            #if role is None:
                #await ctx.guild.create_role(name="Valorant | "+player_cur_rank, color=color)
            #role = discord.utils.get(ctx.guild.roles, name="Valorant | "+player_cur_rank)
            #await ctx.author.add_role(role)
        await print("success")
    except ValueError as e:
        print(str(e))
        #await ctx.send(str(e))

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