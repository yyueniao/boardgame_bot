import discord
from discord.ext import commands
import json
import re
import random

from cmds.main import Main
from core.classes import Cog_Extension

with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class COC(Cog_Extension):
    players = {}
    state = "close"


    @commands.command()
    async def start(self, ctx):
        COC.state = "start"
        await ctx.send("游戏开始！")

    @commands.command()
    async def st(self, ctx, skill):
        if COC.state != "start":
            ctx.send("请先开始游戏。回复'-start'立即开始游戏。")
            return 0
        res = re.findall(r'[0-9]+|[a-z,\u4e00-\u9fa5]+', skill)
        if not ctx.message.author in COC.players:
            player_info = {}
        else:
            player_info = COC.players[ctx.message.author]
        i = 0
        while i < len(res):
            try:
                player_info[res[i]] = int(res[i+1])
                i += 2
            except:
                print(res[i+1])

        COC.players[ctx.message.author] = player_info
        await ctx.send(f"{ctx.message.author.name}设置技能成功")

    @commands.command()
    async def cp(self, ctx, name):
        if COC.state != "start":
            ctx.send("请先开始游戏。回复'-start'立即开始游戏。")
            return 0
        player_info = COC.players[ctx.message.author]
        target = player_info[name]
        await ctx.send(f"你的'{name}'为{target}")


    @commands.command()
    async def ra(self, ctx, name):
        player_info = COC.players[ctx.message.author]
        target = player_info[name]
        diff = int(target/2)
        sup = int(target/5)
        point = random.randint(1, 100)
        if point <= 1:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，达成了大成功！")
        elif point <= sup:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，达成了极难成功！")
        elif point <= diff:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，达成了困难成功！")
        elif point <= target:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，达成了普通成功！")
        elif (point > 95 and target < 50) or point == 100:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，导致了大失败！")
        else:
            await ctx.send(f"'{name}'检定（{target}）：你丢出了{point}，导致了普通失败！")



def setup(bot):
    bot.add_cog(COC(bot))