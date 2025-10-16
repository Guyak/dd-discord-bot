from json import load as j_load
import discord
from discord.ext import commands
from lib_twitch_data_fetcher import get_dict_from_stream, StreamNotLiveError



##————————————————————————————————————————————————————————————————————————————##

bot = commands.Bot()

##————————————————————————————————————————————————————————————————————————————##

config_file = "_config_available_server.json"
with open(config_file) as file:
    credentials = j_load(file)

serv_DD = credentials["serv_DD"]
stream_channel_DD = credentials["stream_channel_DD"]
in_use_DD = credentials["in_use_DD"]
serv_Guyal = credentials["serv_Guyal"]
stream_channel_Guyal = credentials["stream_channel_Guyal"]
in_use_Guyal = credentials["in_use_Guyal"]
serv_HR = credentials["serv_HR"]
stream_channel_HR = credentials["stream_channel_HR"]
in_use_HR = credentials["in_use_HR"]

def guild_id(use_DD, use_Guyal, use_HR):
    id = []

    if use_DD and in_use_DD:
        id.append(serv_DD)
    if use_Guyal and in_use_Guyal:
        id.append(serv_Guyal)
    if use_HR and in_use_HR:
        id.append(serv_HR)
    
    return id

##————————————————————————————————————————————————————————————————————————————##

# From https://stackoverflow.com/questions/71165431/ , "pycord version" :
# Add the guild ids in which the slash command will appear.
# If it should be in all, remove the argument, but note that it will take some
# time (up to an hour) to register the command if it's for all guilds.

@bot.slash_command(
    name="first_slash",
    description="This is the first slash command.",
    guild_ids=guild_id(True, True, False),
)
async def first_slash(ctx):
    await ctx.respond("You executed the slash command!")



@bot.slash_command(
    name="second_slash",
    description="This is the second slash command.",
    guild_ids=guild_id(True, True, False),
)
async def second_slash(
        ctx, value: str = discord.Option(description="What I will echo")
    ):
    await ctx.respond(f"{value}")



@bot.slash_command(
    name="user_info",
    description="Get information about the user executing the command.",
    guild_ids=guild_id(True, True, False),
)
async def user_info(ctx):
    user_id = ctx.author.id     # User ID
    username = ctx.author.name  # User name
    nickname = ctx.author.nick  # User nickname (None if not set)
    guild = ctx.guild.id

    output = f"User ID: {user_id} \nUsername: {username} \n\
        Nickname: {nickname or 'No nickname set'} \n\
        Guild ID: {guild}"

    await ctx.respond(output)



@bot.slash_command(
    name="stream_announcement",
    description="Annoncer un stream.",
    guild_ids=guild_id(True, True, True),
)
async def stream_announcement(
        ctx,
        chaine: str = discord.Option(description=
                                            "Le nom de la chaine Twitch - Par défaut : harmoniamk",
                                    default=
                                            "harmoniamk"
                                            ),
        pseudo: str = discord.Option(description=
                                            "Optionnel - Le pseudo à afficher dans le message",
                                    required=False
                                            )
    ):
    await ctx.defer()

    config_file = "_config_twitch_api.json"
    if ctx.guild.id == serv_DD: # If serv DD
        channel = bot.get_channel(stream_channel_DD) # Send the message to #general
    if ctx.guild.id == serv_Guyal: # If serv Guyal
        channel = bot.get_channel(stream_channel_Guyal) # Send the message to #general
    if ctx.guild.id == serv_HR:    # If serv HR
        channel = bot.get_channel(stream_channel_HR) # Send the message to #annonces

    user_nickname = pseudo or ctx.author.nick
    user_username = ctx.author.name # Use the username if the nickname is empty

    url = f"https://www.twitch.tv/{chaine}" # Generate the channel URL

    dict_error = False
    try :
        info_dict = get_dict_from_stream(chaine, config_file)
    except StreamNotLiveError:
        dict_error = True

    if dict_error:
        output = f"""
        ***EN LIVE***
**{user_nickname or user_username}** est très bientôt en stream !
{url}
    """
        await channel.send(output)
        await ctx.respond("Annonce envoyée ! (*version __stream pas encore lancé__*)", ephemeral=True)
    else:
        title = info_dict["stream_title"]
        game = info_dict["game_name"]

        output = f"""
        ***EN LIVE***
**{user_nickname or user_username}** est en stream sur __{game}__ !
**{title}**
{url}
        """
        await channel.send(output)
        await ctx.respond("Annonce envoyée !", ephemeral=True)



##————————————————————————————————————————————————————————————————————————————##

if (__name__ == "__main__"):
    config_file = "_config_discord_api.json"

    with open(config_file) as file:
        credentials = j_load(file)

    discord_bot_token = credentials["discord_bot_token"]

    print("Running…")
    bot.run(discord_bot_token)


