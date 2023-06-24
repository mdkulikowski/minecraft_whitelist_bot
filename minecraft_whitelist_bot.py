# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import discord
import json
import subprocess
from dotenv import dotenv_values

##### data###############
env_vars = dotenv_values('secrets.env')
TOKEN = env_vars['TOKEN_ID']
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
########################

##### functions##########


# check if duplicates
def duplicate(json_data, name):
    for entrie in json_data:
        if entrie['name'] == name:
            return True
    return False


def attempt_write_to_whitelist(message, name):
    whitelist_path = 'data/whitelist.json'
    # open file(filename)
    with open(whitelist_path) as file:
        data = json.load(file)

# print error or write to json
    if (not duplicate(data, name)):
        new_data = {}
        new_data['name'] = name
        data.append(new_data)
        with open(whitelist_path, 'w') as file:
            json.dump(data, file)
        message.channel.send(
            "Registered user in whitelist...Server will now restart")
        subprocess.run(["./data/restart_server.sh"])

    else:
        message.channel.send(
            name, ' = Duplicate name detected, will not restart')


########################


client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Minecraft_Whitelist_Bot is Online!')


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.Thread):
        thread_id = env_vars['THREAD_ID']  # Minecraft Whitelist Thread
        print(message.channel.id)
        if message.channel.id == int(thread_id):
            print("its a match")
            attempt_write_to_whitelist(message, message.content)


try:
    client.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
