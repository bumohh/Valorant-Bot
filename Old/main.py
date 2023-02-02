import interactions
import discord
import asyncio
import logging
from variables import discord_token
import time
import discord_methods
import config_methods as config
import network_handler as network
import task_handler as taskHandler


logging.basicConfig(filename='logs\debug-'+str(time.time())+'.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

bot = interactions.Client(discord_token)
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
handler = taskHandler.TaskHandler()

#discord events
@bot.event
async def on_ready():
    #WIP
    guild = client.get_guild(1056830364275982347)
    member = guild.get_member(184886547693174800)
    await discord_methods.updateDiscordRankInternal(guild.get_member(member))
    handler.__init__(asyncio.create_task(discord_methods.updater()))
    pass
            
    
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
        
        logging.debug("starting adder_command function")
        
        data = network.fetchDataForUser(region, name, tag)

        discord_methods.save_data(ctx, data, region)
        
        await discord_methods.updateDiscordRank(ctx, data)
        
        #handler.startNewTask(asyncio.create_task(discord_methods.updater()))
    except ValueError as e:
        await ctx.send(str(e))
    
config.internalSoftReset()
bot.start()