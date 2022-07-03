import discord
from discord.ext import commands
import json
import asyncio

from cmds.main import Main
from core.classes import Cog_Extension
import numpy as np


class Liar(Cog_Extension):
    players = []
    character = {}
    money = {}
    msg = {}
    started = False

    @commands.command()
    async def start(self, ctx):
        if Liar.started:
            return 0
        if len(Main.players) < 2 or len(Main.players) > 9999:
            await ctx.send("人数不符合游戏要求!")
            return 0
        players = Main.players
        np.random.shuffle(players)
        Liar.players = players
        Liar.started = True
        await self.game_setup(ctx)

    async def game_setup(self, ctx):
        desk = []
        char = ["刺客", "守卫", "侦探", "投资人", "官员"]
        for i in range(5):
            for j in range(int(len(Liar.players) * 2 / 5) + 1):
                desk.append(char[i])
        np.random.shuffle(desk)
        for i in range(len(Liar.players)):
            Liar.character[str(Liar.players[i].id)] = [desk[2 * i], desk[2 * i + 1]]
            Liar.money[str(Liar.players[i].id)] = 1
            m = await self.check(ctx, Liar.players[i])
            Liar.msg[str(Liar.players[i].id)] = m
        Liar.character["desk"] = desk[len(Liar.players) * 2:]
        arrange = ""
        for player in Liar.players:
            arrange += player.name + " "
        title = ">>Liar<<"
        desc = " "
        embed = discord.Embed(title=title,description=desc)
        for i in range(len(Liar.players)):
            val = f"玩家：{Liar.players[i].name}\n身份牌：2\n金：1"
            embed.add_field(name=f"{str(i + 1)}号位", value=val, inline=True)
        embed.add_field(name=f"牌堆：",value=f"{len(Liar.character['desk'])}",inline=True)
        msg = await ctx.send(embed=embed)
        Liar.msg["public"] = msg

    async def check(self, ctx, user=None):
        if not user:
            user = ctx.message.author
        m = await user.send(f"你手上的牌是{Liar.character[str(user.id)]}，你拥有{Liar.money[str(user.id)]}金。")
        return m

    @commands.command()
    async def watch(self, ctx, target_mention):
        target_id = target_mention[3:-1]
        target = await self.bot.fetch_user(int(target_id))
        rand = [0,1]
        np.random.shuffle(rand)
        res = rand[0]
        if len(Liar.character[str(target_id)]) == 1:
            res = 0
        await ctx.send(f"{ctx.message.author.name}查看了{target.name}的一张身份牌")
        await self.update(ctx.message.author, f"你看到{target.name}是{Liar.character[str(target_id)][res]}")
        await self.update(target, f"你的{Liar.character[str(target_id)][res]}被{ctx.message.author.name}看见了！")

    @commands.command()
    async def board(self, ctx):
        msg_original = Liar.msg["public"]
        await msg_original.delete()
        title = ">>Liar<<"
        desc = " "
        embed = discord.Embed(title=title, description=desc)
        for i in range(len(Liar.players)):
            val = f"玩家：{Liar.players[i].name}\n身份牌：{len(Liar.character[str(Liar.players[i].id)])}\n金：{Liar.money[str(Liar.players[i].id)]}"
            embed.add_field(name=f"{str(i + 1)}号位", value=val, inline=True)
        embed.add_field(name=f"牌堆：",value=f"{len(Liar.character['desk'])}",inline=True)
        msg = await ctx.send(embed=embed)
        Liar.msg["public"] = msg

    @commands.command()
    async def proof(self, ctx, card):
        if card in Liar.character[str(ctx.message.author.id)]:
            await ctx.send(f"{ctx.message.author.name}拥有{card}！")
        else:
            await ctx.send(f"{ctx.message.author.name}没有{card}！")

    async def update(self, user, content_addon=""):
        await Liar.msg[str(user.id)].edit(content=f"你手上的牌是{Liar.character[str(user.id)]}，你拥有{Liar.money[str(user.id)]}金。\n{content_addon}")
        title = ">>Liar<<"
        desc = " "
        embed = discord.Embed(title=title, description=desc)
        for i in range(len(Liar.players)):
            val = f"玩家：{Liar.players[i].name}\n身份牌：{len(Liar.character[str(Liar.players[i].id)])}\n金：{Liar.money[str(Liar.players[i].id)]}"
            embed.add_field(name=f"{str(i + 1)}号位", value=val, inline=True)
        embed.add_field(name=f"牌堆：",value=f"{len(Liar.character['desk'])}",inline=True)
        await Liar.msg["public"].edit(embed=embed)

    @commands.command()
    async def give(self, ctx, target="", num='0'):
        giver = ctx.message.author
        recipient_id = target[3:-1]
        recipient = await self.bot.fetch_user(int(recipient_id))
        if int(Liar.money[str(giver.id)]) < int(num):
            await ctx.send("你没有这么多钱哦~")
            return 0

        Liar.money[str(giver.id)] -= int(num)
        Liar.money[str(recipient_id)] += int(num)
        await ctx.send(f"{giver.name}给了{recipient.name}{num}金。")
        await self.update(giver)
        await self.update(recipient)

    @commands.command()
    async def dead(self, ctx, index=None):
            user = ctx.message.author
            if len(Liar.character[str(user.id)]) == 1:
                dead_card = Liar.character[str(user.id)][0]
                Liar.character[str(user.id)] = []
            elif index == '1':
                dead_card = Liar.character[str(user.id)][0]
                Liar.character[str(user.id)] = [Liar.character[str(user.id)][1]]
            elif index == '2':
                dead_card = Liar.character[str(user.id)][1]
                Liar.character[str(user.id)] = [Liar.character[str(user.id)][0]]
            else:
                await ctx.send("请使用‘*dead [i]’放弃第i张身份牌，如：‘*dead 2’")
                return 0
            Liar.character["desk"].append(dead_card)
            np.random.shuffle(Liar.character["desk"])
            await ctx.send(f"{user.name}失去一张身份牌")
            await self.update(user)


    @commands.command()
    async def get(self, ctx, num = '0'):
            user = ctx.message.author
            Liar.money[str(user.id)] += int(num)
            await ctx.send(f"{user.name}得到了{num}金。")
            await self.update(user)


    @commands.command()
    async def spend(self, ctx, num = '0'):
            user = ctx.message.author
            if Liar.money[str(user.id)] < int(num):
                await ctx.send("你没有这么多钱哦~")
                return 0
            Liar.money[str(user.id)] -= int(num)
            await ctx.send(f"{user.name}花掉了{num}金。")
            await self.update(user)


    @commands.command()
    async def change(self, ctx, index = None):
            user = ctx.message.author
            if len(Liar.character[str(user.id)]) == 1:
                dead_card = Liar.character[str(user.id)][0]
                Liar.character[str(user.id)] = [Liar.character['desk'][0]]
            elif index == '1':
                dead_card = Liar.character[str(user.id)][0]
                Liar.character[str(user.id)] = [Liar.character[str(user.id)][1], Liar.character['desk'][0]]
            elif index == '2':
                dead_card = Liar.character[str(user.id)][1]
                Liar.character[str(user.id)] = [Liar.character[str(user.id)][0], Liar.character['desk'][0]]
            else:
                await ctx.send("请使用‘*change [i]’换掉第i张身份牌，如：‘*change 2’")
                return 0
            Liar.character['desk'].append(dead_card)
            np.random.shuffle(Liar.character['desk'])
            await ctx.send(f"{user.name}换掉1张身份牌。")
            await self.update(user)



def setup(bot):
    bot.add_cog(Liar(bot))
