import discord
from discord.ext import commands
import json
from core.classes import Cog_Extension
import re


with open("setting.json",'r',encoding='utf8') as jfile:
    jdata = json.load(jfile)

class Main(Cog_Extension):
    game = None
    players = []
    room_info = None
    room_msg = None
    state = "free"



    @commands.command()
    async def gamelist(self, ctx):
        print('>>打开游戏列表<<')
        embed = discord.Embed(title=">>游戏列表<<", description="下列为已开发的游戏！更多游戏正在开发中~")
        games = jdata["gamelist"]
        index = 1
        for game in games:
            embed.add_field(name=str(index), value=game, inline=False)
            index += 1
        embed.set_footer(text="输入 '-open [游戏名称]' 立即开启游戏房间\n例：’-open 刺杀国王‘")
        await ctx.send(embed=embed)
        print(">>游戏列表已开启<<")

    @commands.command()
    async def open(self, ctx, game=None):
        print("check if format is correct:")
        if game == None:
            await ctx.send("请输入游戏名称。\n例：’-open 刺杀国王‘")
            return 0
        if game not in jdata["gamelist"]:
            await ctx.send(f"对不起啦，{game} 还没开发完成，输入'-gamelist'看看这里有什么游戏~")
            return 0

        print("check if there is another room already")
        if Main.state != "free":
            await ctx.send("暂时只能开启一个房间~请先回复'-close'关闭先前的房间，然后再次使用本指令")
            return 0

        print("opening the room")
        Main.game = game
        print(f"set {Main.game} success")
        details = jdata["details"]
        detail = details[game]
        self.bot.load_extension(f"games.{detail['filename']}")
        print(f"loaded game file success")
        embed = discord.Embed(title=f">>{game}<<", description=f"{detail['introduction']}")
        embed.add_field(name="游戏人数", value=f"{detail['min']}~{detail['max']}", inline=False)
        embed.add_field(name="游戏时长", value=detail['time'], inline=False)
        embed.add_field(name="玩家", value="无", inline=False)
        embed.set_footer(text=f"要加入游戏，请回复'-join'\n要退出游戏，请回复'-quit'\n要开始游戏，请回复'-start'\n要关闭房间，请回复"
                              f"'-close'")
        msg = await ctx.send(embed=embed)
        Main.room_info = embed
        Main.room_msg = msg
        Main.state = "open"
        print("open room success")

    @commands.command()
    async def join(self, ctx):
        if Main.state != "open":
            await ctx.send("没有已开启的游戏，请先开启游戏房间。输入 '-open [游戏名称]' 立即开启游戏房间\n例：’-open 刺杀国王‘")
            return 0
        print("check if he/she has not joined")
 #       if ctx.message.author in Main.players:
  #          await ctx.message.delete()
   #         return 0
        print("joining")
        Main.players.append(ctx.message.author)
        players_name = ""
        embed = Main.room_info
        msg = Main.room_msg
        for pl in Main.players:
            players_name += pl.name + "\n"
        embed.set_field_at(index=2, name="玩家", value=players_name, inline=False)
        await msg.edit(embed=embed)
        print("join success")


    @commands.command()
    async def quit(self, ctx):
        if Main.state != "open":
            return 0
        if not ctx.message.author in Main.players:
            await ctx.message.delete()
            return 0
        print("quitting")
        Main.players.remove(ctx.message.author)
        players_name = ""
        embed = Main.room_info
        msg = Main.room_msg
        for pl in Main.players:
            players_name += pl.name + "\n"
        if len(Main.players) == 0:
            players_name = "无"
        embed.set_field_at(index=2, name="玩家", value=players_name, inline=False)
        await msg.edit(embed=embed)
        print("quit success")

    @commands.command()
    async def close(self, ctx):
        print("check if there was room opened")
        if Main.state != "open":
            ctx.send("当前没有已开启的房间，现在就来开个房间玩玩吧！\n请输入格式：'bg-open [游戏]'\n例：'bg-open 刺杀国王'")
            return 0
        print("closing...")
        Main.players = []
        details = jdata["details"]
        detail = details[Main.game]
        self.bot.unload_extension(f"games.{detail['filename']}")
        Main.room_info = None
        Main.room_msg = None
        await ctx.send(f"{Main.game}-房间已关闭")
        Main.game = None
        Main.state = "free"




def setup(bot):
    bot.add_cog(Main(bot))