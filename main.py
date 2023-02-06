################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#  _                                 _                                                                                                                                                                         #
# (_) _ __ ___   _ __    ___   _ __ | |_  ___                                                                                                                                                                  #
# | || '_ ` _ \ | '_ \  / _ \ | '__|| __|/ __|                                                                                                                                                                 #
# | || | | | | || |_) || (_) || |   | |_ \__ \                                                                                                                                                                 #
# |_||_| |_| |_|| .__/  \___/ |_|    \__||___/                                                                                                                                                                 #
#               |_|                                                                                                                                                                                            #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################
# Discord
import discord
from discord import app_commands
from discord.app_commands import Choice
# External
import asyncio
import re
import datetime
# Internal
import log
import on_ready_functions
import slash_functions
from variables import *
import help_desc








################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                              _                                                                                                                                                               #
#   ___   _ __          _ __   ___   __ _   __| | _   _                                                                                                                                                        #
#  / _ \ | '_ \        | '__| / _ \ / _` | / _` || | | |                                                                                                                                                       #
# | (_) || | | |       | |   |  __/| (_| || (_| || |_| |                                                                                                                                                       #
#  \___/ |_| |_| _____ |_|    \___| \__,_| \__,_| \__, |                                                                                                                                                       #
#               |_____|                           |___/                                                                                                                                                        #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################

class aclient(discord.Client):
    
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        global narberals_verifier_role_id
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=guild_id))
            self.synced = True
        log.debug(f"We have logged in as {self.user}.")
        # Created Narberals Verifier Role
        server = client.get_guild(guild_id)
        role = discord.utils.get(server.roles, name="Narberals Verifier")
        if not role:
            role = await server.create_role(name="Narberals Verifier")
        bot = server.get_member(client.user.id)
        if bot.top_role.position > 0:
            await role.edit(position=bot.top_role.position - 1)
        else:
            await role.edit(position=0)
        narberals_verifier_role_id = role.id

        on_ready_functions.initDatabase()
        while True:
            if on_ready_functions.isDatabaseEmpty():
                await asyncio.sleep(1) 
            else:
                # Main on_ready loop grabs database and loops through the data one per every 10 seconds so api call should only be 6 per minute max.
                for data in on_ready_functions.readDatabase():
                    discord_id, region, ign, tag, rank_full, puuid, verification_status = data
                    log.debug("Calling Regular Valorant API for "+ str(ign)+" #"+str(tag)+".")
                    regularValApiCall_results = on_ready_functions.regularValApiCall(region, puuid)
                    pulled_rank_full = regularValApiCall_results[0]
                    pulled_ign = regularValApiCall_results[1]
                    pulled_tag = regularValApiCall_results[2]
                    if str(pulled_rank_full) != str(rank_full):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    elif str(pulled_ign) != str(ign):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    elif str(pulled_tag) != str(pulled_tag):
                        on_ready_functions.updateDatabase(pulled_rank_full, pulled_ign, pulled_tag, discord_id, puuid)
                    log.debug("Status: "+verification_status)
                    # check if user has roled call rank_full
                    if verification_status == "Verified":
                        guild = discord.utils.get(client.guilds, id=guild_id)
                        member = discord.utils.get(guild.members, id=int(discord_id))
                        role_list = member.roles
                        if str(pulled_rank_full) != str(rank_full) or pulled_rank_full not in str(role_list):
                            log.debug("pulled_rank_full did not equal "+str(pulled_rank_full)+" rank_full " + str(rank_full)+".")
                            # Sorts pulled_rank_full into variables for setting and creating
                            if pulled_rank_full == None :
                                    rank_short = "Unranked"
                                    pulled_rank_full = "Unranked"
                            else:
                                rank_short = ' '.join(pulled_rank_full.split()[:-1])

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
                            color = ranks[rank_short].value
                            guild = discord.utils.get(client.guilds, id=guild_id)
                            member = discord.utils.get(guild.members, id=int(discord_id))


                            
                            role_name = "Valorant | " + pulled_rank_full
                            role = discord.utils.get(guild.roles, name=role_name)
                            if not role:
                                role = await guild.create_role(name=role_name,color=color)
                            if rank_full not in str(role_list):
                                pass
                            else:
                                old_role_name = "Valorant | " + rank_full
                                old_role = discord.utils.get(guild.roles, name=old_role_name)
                                await member.remove_roles(old_role)
                                log.debug("removed old role called "+str(old_role)+" and replaced with "+role+".")
                                
                            await member.add_roles(role)
                            log.debug("Added Role "+role_name+".")
                    else:
                        pass
                    await asyncio.sleep(10)

client = aclient()
tree = app_commands.CommandTree(client)








################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _         _                       _     _                                  _      _                                                        _                                            #
#    / /__   __  __ _ | |       | |_  _ __   __ _   ___ | | __(_) _ __    __ _          __ _   __| |  __| |   ___   ___   _ __ ___   _ __ ___    __ _  _ __    __| |                                           #
#   / / \ \ / / / _` || | _____ | __|| '__| / _` | / __|| |/ /| || '_ \  / _` | _____  / _` | / _` | / _` |  / __| / _ \ | '_ ` _ \ | '_ ` _ \  / _` || '_ \  / _` |                                           #
#  / /   \ V / | (_| || ||_____|| |_ | |   | (_| || (__ |   < | || | | || (_| ||_____|| (_| || (_| || (_| | | (__ | (_) || | | | | || | | | | || (_| || | | || (_| |                                           #
# /_/     \_/   \__,_||_|        \__||_|    \__,_| \___||_|\_\|_||_| |_| \__, |        \__,_| \__,_| \__,_|  \___| \___/ |_| |_| |_||_| |_| |_| \__,_||_| |_| \__,_|                                           #
#                                                                        |___/                                                                                                                                 #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################

@app_commands.choices(region = [
    Choice(name="NA", value="NA"),
    Choice(name="EU", value="EU"),
    Choice(name="KR", value="KR")
    ]
)

# /val-tracking-add command
@tree.command(guild = discord.Object(id=guild_id), name = 'val-tracking-add', description='Command for Valorant role syncing and tracking.')
async def valTrackingAddCommand(interaction: discord.Interaction, region: str, name: str, tag: str):
    await interaction.response.defer(ephemeral=True)
    discord_id = str(interaction.user.id)
    
    # Rename to read easier
    ign = name
    
    # External helper functions
    initialValApiCall_results = slash_functions.InitialValApiCall(region, ign, tag)
    bannerValApiCall_results = slash_functions.bannerValApiCall(ign, tag)[0]
    pulled_rank_full = initialValApiCall_results[0]
    puuid = initialValApiCall_results[1]
    rank_image = initialValApiCall_results[2]
    
    if slash_functions.duplicateCheck(puuid):
        guild = interaction.guild
        user = interaction.user
        member = guild.get_member(user.id)
        await interaction.followup.send("The Valorant account under " +ign+" #"+tag+" appears to have already be linked to a Discord account.")
    
    else:
        slash_functions.initialDatabaseSave(discord_id, region, ign, tag, pulled_rank_full, puuid, "Pending")
        
        # Sorts pulled_rank_full into variables for setting and creating
        if pulled_rank_full == None :
                rank_short = "Unranked"
                pulled_rank_full = "Unranked"
        else:
            rank_short = ' '.join(pulled_rank_full.split()[:-1])

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

        color = ranks[rank_short].value
        
        embed = discord.Embed(title="Valorant Account Submitted:", color=color)
        if rank_short == "Unranked": 
            embed.set_thumbnail(url="https://www.metasrc.com/assets/v/3.25.2/images/valorant/ranks/unranked.png")
        else:
            embed.set_thumbnail(url=f"{rank_image}")
        embed.set_image(url=f"{bannerValApiCall_results}")
        embed.add_field(name="Region:", value=region, inline=True)
        embed.add_field(name="Username:", value=name, inline=True)
        embed.add_field(name="Tag:", value=tag, inline=True)
        embed.add_field(name="Rank:", value=pulled_rank_full, inline=True)
        embed.add_field(name="Verification Status:",value="Pending", inline=True)

        await interaction.followup.send(embed=embed)








#################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _                                                _                    _             _                                   _   __  _               _    _                                  #
#    / /__   __  __ _ | |        _ __ ___    __ _  _ __   _   _   __ _ | |         __ _   __| | _ __ ___  (_) _ __         __   __  ___  _ __ (_) / _|(_)  ___   __ _ | |_ (_)  ___   _ __                     #
#   / / \ \ / / / _` || | _____ | '_ ` _ \  / _` || '_ \ | | | | / _` || | _____  / _` | / _` || '_ ` _ \ | || '_ \  _____ \ \ / / / _ \| '__|| || |_ | | / __| / _` || __|| | / _ \ | '_ \                    #
#  / /   \ V / | (_| || ||_____|| | | | | || (_| || | | || |_| || (_| || ||_____|| (_| || (_| || | | | | || || | | ||_____| \ V / |  __/| |   | ||  _|| || (__ | (_| || |_ | || (_) || | | |                   #
# /_/     \_/   \__,_||_|       |_| |_| |_| \__,_||_| |_| \__,_| \__,_||_|        \__,_| \__,_||_| |_| |_||_||_| |_|         \_/   \___||_|   |_||_|  |_| \___| \__,_| \__||_| \___/ |_| |_|                   #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################
# /val-manual-admin-verification
@tree.command(guild = discord.Object(id=guild_id), name = 'val-manual-admin-verification', description='Command for admins to quickly verify a users account.')
async def valAdminSetAccountVerifed(interaction: discord.Interaction, name: str):
    await interaction.response.defer(ephemeral=False)
    server = client.get_guild(guild_id)
    role = discord.utils.get(server.roles, id=narberals_verifier_role_id)
    members = [member for member in server.members if role in member.roles]
    for member in members:
        if interaction.user.id == member.id:
            discord_id = int(re.search(r'\d+', str(name)).group())
            slash_functions.updateVerifiedStatusInDatabase(discord_id, "Verified")
            await interaction.followup.send('Successfully verified all Valorant accounts connected to '+str(name)+".")
            break
    else:
        await interaction.followup.send('You do not have the required permissions to use this command, to get verified please either wait for an admin or use the "Banner Method".')








################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _         _                                                                 _   __  _               _    _                                                                              #
#    / /__   __  __ _ | |       | |__    __ _  _ __   _ __    ___  _ __        __   __  ___  _ __ (_) / _|(_)  ___   __ _ | |_ (_)  ___   _ __                                                                 #
#   / / \ \ / / / _` || | _____ | '_ \  / _` || '_ \ | '_ \  / _ \| '__| _____ \ \ / / / _ \| '__|| || |_ | | / __| / _` || __|| | / _ \ | '_ \                                                                #
#  / /   \ V / | (_| || ||_____|| |_) || (_| || | | || | | ||  __/| |   |_____| \ V / |  __/| |   | ||  _|| || (__ | (_| || |_ | || (_) || | | |                                                               #
# /_/     \_/   \__,_||_|       |_.__/  \__,_||_| |_||_| |_| \___||_|            \_/   \___||_|   |_||_|  |_| \___| \__,_| \__||_| \___/ |_| |_|                                                               #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################
@app_commands.choices(step = [
    Choice(name="1", value="1"),
    Choice(name="2", value="2"),
    Choice(name="3", value="3")
    ]
)

# /val-banner-verification
@tree.command(guild = discord.Object(id=guild_id), name = 'val-banner-verification', description="Command for users to self verify accounts. If it's your first time please use /val-tracking-help.")
async def valBannerSetAccountVerifed(interaction: discord.Interaction, step: str, name: str, tag: str):
    await interaction.response.defer(ephemeral=True)
    discord_id = interaction.user.id
    current_time = datetime.datetime.now().time().strftime("%Y-%m-%d %H:%M:%S")
    if step == "1":
        step_1_banner = str(slash_functions.bannerValApiCall(name,tag)[1])
        slash_functions.updateBannerVerificationStepOneDatabase(discord_id, name, tag, step_1_banner, current_time)
        await interaction.followup.send("Step 1 complete. Please swap your banner to any random banner and go into a custom game and surrender as soon as possible, then enter command again and select step 2.")
    elif step == "2":
        get_banner_data = slash_functions.getBannerVerificationDataFromDatabase(discord_id, name, tag)
        step_1_banner = get_banner_data[0]
        step_2_banner = str(slash_functions.bannerValApiCall(name,tag)[1])
        if step_1_banner == step_2_banner:
            slash_functions.removeVerificationDataFromDatabase(discord_id, name, tag)
            await interaction.followup.send("Banner swap was not done correctly. Banner verification incomplete. Please restart.")
        if step_1_banner != step_2_banner:
            slash_functions.updateBannerVerificationStepTwoDatabase(discord_id, name, tag, step_2_banner)
            await interaction.followup.send("Step 2 complete. Please swap banners back to the first one you had on before step 1, go into another custom game and surrender as soon as possible, then enter the command again and select step 3 to finish.")
    elif step == "3":
        get_banner_data = slash_functions.getBannerVerificationDataFromDatabase(discord_id, name, tag)
        step_1_banner = get_banner_data[0]
        start_time = get_banner_data[1]
        step_2_banner = get_banner_data[2]
        step_3_banner = str(slash_functions.bannerValApiCall(name,tag)[1])
        datetime1 = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        datetime2 = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        delta = datetime2 - datetime1
        minutes = delta.total_seconds() / 60

        if step_3_banner ==  step_1_banner and step_3_banner != step_2_banner and int(minutes) < 60:
            slash_functions.updateVerifiedStatusInDatabase(discord_id, "Verified")
            slash_functions.removeVerificationDataFromDatabase(discord_id, name, tag)
            await interaction.followup.send("Banner verification complete!")
        elif step_3_banner ==  step_1_banner and step_3_banner != step_2_banner and int(minutes) > 60:
            slash_functions.removeVerificationDataFromDatabase(discord_id, name, tag)
            await interaction.followup.send("1 hour time limit exceeded. Banner verification incomplete. Please restart.")
        elif step_3_banner !=  step_1_banner:
            slash_functions.removeVerificationDataFromDatabase(discord_id, name, tag)
            await interaction.followup.send("Banner swap was not done correctly. Banner verification incomplete. Please restart.")
        # Tell user sucess
    else:
        # Dosen't actually contact a dev right now will set in future*
        await interaction.followup.send("Something is wrong, automaticlly contacting a dev.")








################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _                                                 _                                                 _                                                                                   #
#    / /__   __  __ _ | |         __ _   ___   ___   ___   _   _  _ __  | |_  ___          ___  __   __  ___  _ __ __   __(_)  ___ __      __                                                                  #
#   / / \ \ / / / _` || | _____  / _` | / __| / __| / _ \ | | | || '_ \ | __|/ __| _____  / _ \ \ \ / / / _ \| '__|\ \ / /| | / _ \\ \ /\ / /                                                                  #
#  / /   \ V / | (_| || ||_____|| (_| || (__ | (__ | (_) || |_| || | | || |_ \__ \|_____|| (_) | \ V / |  __/| |    \ V / | ||  __/ \ V  V /                                                                   #
# /_/     \_/   \__,_||_|        \__,_| \___| \___| \___/  \__,_||_| |_| \__||___/        \___/   \_/   \___||_|     \_/  |_| \___|  \_/\_/                                                                    #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################
# /val-accounts-overview command
@tree.command(name = 'val-accounts-overview', description="Command to get overview of Valorant accounts associated with your Discord.", guild = discord.Object(id=guild_id))
async def valAccountsOverview(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    discord_id = interaction.user.id
    fetched_data = slash_functions.getRowsByDiscord_id(discord_id)
    log.debug("fetched_data is: "+str(fetched_data))
    if str(fetched_data) == str([]):
        await interaction.followup.send("No Valorant accounts are currectly connected to your Discord account.")
    else:
        embed_list = []
        for user_id, region, name, tag, rank_full, puuid, verification_status in fetched_data:
            InitialValApiCall_results = slash_functions.InitialValApiCall(region, name, tag)
            try:
                getValMatchDataApiCall_results = slash_functions.getValMatchDataApiCall(region, name, tag)
            except:
                pass
            rank_rating = InitialValApiCall_results[4] 
            elo = InitialValApiCall_results[3]
            rank_image = InitialValApiCall_results[2]
            banner_image = str(slash_functions.bannerValApiCall(name, tag)[0])
            # Sorts pulled_rank_full into variables for setting and creating
            if rank_full == None :
                    rank_short = "Unranked"
                    rank_full = "Unranked"
            else:
                rank_short = ' '.join(rank_full.split()[:-1])

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
            
            role_name = "Valorant | " + rank_full
            color = ranks[rank_short].value
            
            embed = discord.Embed(title="Overview of Valorant Accounts:", color=color)
            if rank_short == "Unranked": 
                embed.set_thumbnail(url="https://www.metasrc.com/assets/v/3.25.2/images/valorant/ranks/unranked.png")
            else:
                embed.set_thumbnail(url=f"{rank_image}")
            embed.set_image(url=f"{banner_image}")
            embed.add_field(name="Region:", value=region, inline=True)
            embed.add_field(name="Username:", value=name, inline=True)
            embed.add_field(name="Tag:", value=tag, inline=True)
            embed.add_field(name="Rank:", value=rank_full, inline=True)
            if verification_status == "Verified":
                embed.add_field(name="Rank Rating:",value=rank_rating, inline=True)
                embed.add_field(name="Elo:",value=elo, inline=True)
                embed.add_field(name="Average Headshot:",value=getValMatchDataApiCall_results[1], inline=True)
                embed.add_field(name="Average Bodyshot:",value=getValMatchDataApiCall_results[2], inline=True)
                embed.add_field(name="Average Legshot:",value=getValMatchDataApiCall_results[3], inline=True)
                embed.add_field(name="Average KDA:",value=getValMatchDataApiCall_results[0], inline=True)
                embed.add_field(name="Winrate:",value=getValMatchDataApiCall_results[4], inline=True)
                
                embed.add_field(name="Added Role:",value=role_name, inline=True)   
            else:
                embed.add_field(name="Verification Status:",value="Pending", inline=True)    
            embed_list.append(embed)   
        await paginate(interaction, embed_list)








################################################################################################################################################################################################################
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _         _            _                                                 _                                                                                                              #
#    / /__   __  __ _ | |       | |__    ___ | | _ __           ___  __   __  ___  _ __ __   __(_)  ___ __      __                                                                                             #
#   / / \ \ / / / _` || | _____ | '_ \  / _ \| || '_ \  _____  / _ \ \ \ / / / _ \| '__|\ \ / /| | / _ \\ \ /\ / /                                                                                             #
#  / /   \ V / | (_| || ||_____|| | | ||  __/| || |_) ||_____|| (_) | \ V / |  __/| |    \ V / | ||  __/ \ V  V /                                                                                              #
# /_/     \_/   \__,_||_|       |_| |_| \___||_|| .__/         \___/   \_/   \___||_|     \_/  |_| \___|  \_/\_/                                                                                               #
#                                               |_|                                                                                                                                                            #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
################################################################################################################################################################################################################
# /val-help-overview command
@tree.command(name = 'val-help-overview', description="Help section for the Valorant commands.", guild = discord.Object(id=guild_id))
async def valHelpOverview(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    image = "https://cdn.publish0x.com/prod/fs/images/6ac0ff5feb2e723eaa18dace82b96ab9aca5ed93038ad2d739f3d58132cc3bed.png"
    embed = discord.Embed(title="Overview of Valorant commands:", color=discord.Colour.from_rgb(245, 166, 35))
    embed.set_thumbnail(url=f"{image}")
    embed.add_field(name="/val-accounts-overview",value=help_desc.val_accounts_overview_desc, inline=False)
    embed.add_field(name="/val-tracking-add",value=help_desc.val_tracking_add_desc, inline=False)
    embed.add_field(name="/val-banner-verification",value=help_desc.val_banner_verification_desc, inline=False)
    embed.add_field(name="/val-manual-admin-verification",value=help_desc.val_manual_admin_verification_desc, inline=False)
    embed.add_field(name="/val-tracking-remove-all",value=help_desc.val_tracking_remove_all_desc, inline=False)
    await interaction.followup.send(embed=embed)








################################################################################################################################################################################################################ 
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#     __               _         _                       _     _                                                                                _  _                                                           #
#    / /__   __  __ _ | |       | |_  _ __   __ _   ___ | | __(_) _ __    __ _         _ __   ___  _ __ ___    ___  __   __  ___          __ _ | || |                                                          #
#   / / \ \ / / / _` || | _____ | __|| '__| / _` | / __|| |/ /| || '_ \  / _` | _____ | '__| / _ \| '_ ` _ \  / _ \ \ \ / / / _ \ _____  / _` || || |                                                          #
#  / /   \ V / | (_| || ||_____|| |_ | |   | (_| || (__ |   < | || | | || (_| ||_____|| |   |  __/| | | | | || (_) | \ V / |  __/|_____|| (_| || || |                                                          #
# /_/     \_/   \__,_||_|        \__||_|    \__,_| \___||_|\_\|_||_| |_| \__, |       |_|    \___||_| |_| |_| \___/   \_/   \___|        \__,_||_||_|                                                          #
#                                                                        |___/                                                                                                                                 #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #
#                                                                                                                                                                                                              #   
################################################################################################################################################################################################################
# /val-tracking-remove-all command
@tree.command(name = 'val-tracking-remove-all', description='Command to remove all Valorant roles from the user.', guild = discord.Object(id=guild_id))
async def removeRoles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    user = interaction.user
    discord_id = user.id
    slash_functions.removeValorantAccountfromDatabase(str(discord_id))
    member = guild.get_member(discord_id)
    roles_to_remove = [role for role in member.roles if 'Valorant |' in role.name]
    for role in roles_to_remove:
        await member.remove_roles(role)
    await interaction.followup.send("All Valorant accounts attached to " +member.name+" #"+member.discriminator+" have been removed.")

async def paginate(interaction, embed_list):
    page_index = 0
    message = await interaction.followup.send(embed=embed_list[page_index])
    pagination_emojis = ("⬅️", "➡️")
    for emoji in pagination_emojis:
        await message.add_reaction(emoji)

    while True:
        reaction, user = await client.wait_for("reaction_add", check=lambda r, u: r.message.id == message.id and str(r.emoji) in pagination_emojis and u != client.user)
        if str(reaction.emoji) == "⬅️":
            page_index -= 1
        else:
            page_index += 1
        if page_index >= len(embed_list):
            page_index = 0
        if page_index < 0:
            page_index = len(embed_list) - 1

        try:
            await message.remove_reaction(reaction.emoji, user)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        await message.edit(embed=embed_list[page_index])

################################################################################################################################################################################################################          
                            #         _ __  _   _  _ __   _ __    ___  _ __                                                                                                                                    #
                            #        | '__|| | | || '_ \ | '_ \  / _ \| '__|                                                                                                                                   #
client.run(discord_token)   #        | |   | |_| || | | || | | ||  __/| |                                                                                                                                      #
                            #        |_|    \__,_||_| |_||_| |_| \___||_|                                                                                                                                      # 
                            #                                                                                                                                                                                  #
################################################################################################################################################################################################################