from discord.ext import commands
import json
import os

with open("setting.json",'r',encoding='utf8') as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix='*')
players = []

@bot.event
async def on_ready():
    print(">>机器人已到场<<")

    
@bot.command()
async def reload(ctx, extension):
    bot.reload_extension(f"{extension}")
    await ctx.send(f"{extension} 更新完成")


for filename in os.listdir('./cmds'):
    if filename.endswith('.py'):
        bot.load_extension(f"cmds.{filename[:-3]}")


if(__name__=="__main__"):
    bot.run(jdata["TOKEN"])
