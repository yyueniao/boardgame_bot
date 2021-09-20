import discord
from discord.ext import commands
import json
import os
import re
from cmds.main import Main

with open("setting.json",'r',encoding='utf8') as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix='-')
players = []

@bot.event
async def on_ready():
    print(">>机器人已到场<<")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cmds.{extension}")
    ctx.send(f"{extension} 加载完成")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cmds.{extension}")
    ctx.send(f"{extension} 卸载完成")

@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"cmds.{extension}")
    ctx.send(f"{extension} 更新完成")



for filename in os.listdir('./cmds'):
    if filename.endswith('.py'):
        bot.load_extension(f"cmds.{filename[:-3]}")


if(__name__=="__main__"):
    bot.run(jdata["TOKEN"])
