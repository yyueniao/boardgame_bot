import discord
from discord.ext import commands
import json
import asyncio

from cmds.main import Main
from core.classes import Cog_Extension
import numpy as np

CHECK_MARK = '✔️'
CROSS_MARK = '❌'

with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)
    details = jdata["details"]
    detail = details["刺杀国王"]


class KillTheKing(Cog_Extension):
    players = []
    character = []
    score = []
    now = 5
    round = 1
    cannot_exchange = -1
    started = False
    waiting_action = False
    king_win = None

    async def close_card(self, ctx, index):
        if KillTheKing.character[index]['show'] == '暗牌':
            return 0
        KillTheKing.character[index]['show'] = '暗牌'
        await ctx.send(f"{KillTheKing.players[index].name}盖上了身份牌。")
        if KillTheKing.character[index]['name'] == '国王':
            await ctx.send(f"由于国王隐藏了身份，所以宣誓主权失败了，游戏继续进行。")
            KillTheKing.king_win = None

    async def open_card(self, ctx, index):
        if KillTheKing.character[index]['show'] != '暗牌':
            return 0
        KillTheKing.character[index]['show'] = KillTheKing.character[index]['name']
        await ctx.send(f"{KillTheKing.players[index].name}公开了身份牌，他的身份是{KillTheKing.character[index]['name']}")
        if KillTheKing.character[index]['name'] == '国王':
            await self.king(ctx)
        if KillTheKing.character[index]['name'] == '奴隶':
            is_end = await self.slave_win_check(ctx)
            if is_end:
                return True
        return False

    def next(self, num):
        newnum = num % len(KillTheKing.players) + 1
        if KillTheKing.character[newnum - 1]["state"] == "死亡":
            return self.next(newnum)
        return newnum

    def bef(self, num):
        if num == 1:
            newnum = len(KillTheKing.players)
        else:
            newnum = num - 1
        if KillTheKing.character[newnum - 1]["state"] == "死亡":
            return self.bef(newnum)
        return newnum

    def exchange(self, a, b):
        temp = KillTheKing.character[a]
        KillTheKing.character[a] = KillTheKing.character[b]
        KillTheKing.character[b] = temp

    async def show_embed(self, ctx, title=None, description=None):
        if not title:
            title = f">>刺杀国王-第{str(KillTheKing.round)}回合<<"
        if not description:
            description = f"轮到了{str(KillTheKing.now)}号位玩家{KillTheKing.players[KillTheKing.now - 1].name}行动，请从以" \
                          f"下动作中选择：\n1. 查看\n2. 交换\n3. 技能"
        embed = discord.Embed(title=title, description=description)
        for i in range(len(KillTheKing.players)):
            val = f"玩家：{KillTheKing.players[i].name}\n手牌：{KillTheKing.character[i]['show']}\n状态：" \
                  f"{KillTheKing.character[i]['state']}"
            if i + 1 == KillTheKing.king_win:
                embed.add_field(name=f"{str(i + 1)}号位👑", value=val, inline=True)
            else:
                embed.add_field(name=f"{str(i + 1)}号位", value=val, inline=True)
        embed.add_field(name=f"{str(len(KillTheKing.players) + 1)}号位", value="（公共区域）\n暗牌", inline=True)
        embed.set_footer(text=f">>请在私聊处确认你的身份<<\n行动格式：'-action [行动]'\n例：'-action 技能'\n")
        await ctx.send(embed=embed)

    async def slave_win_check(self, ctx):
        count = 0
        for i in range(len(KillTheKing.players)):
            if KillTheKing.character[i]['show'] == '奴隶':
                count += 1
                if count >= 3:
                    await self.end(ctx, "革命党")
                    return True
            else:
                count = 0
        j = 0
        if count > 0:
            while KillTheKing.character[j]['show'] == '奴隶':
                count += 1
                if count >= 3:
                    await self.end(ctx, "革命党")
                    return True
                j += 1
        return False

    async def king_win_check(self, ctx):
        count = 0
        for i in range(len(KillTheKing.character)):
            if KillTheKing.character[i]["state"] == '死亡':
                continue
            if KillTheKing.character[i]['name'] == '刺客':
                return 0
            if KillTheKing.character[i]["name"] == '奴隶':
                count += 1
        if count < 3:
            await self.end(ctx, "保皇党")


    async def end(self, ctx, team):
        score_this_round = []
        if team == "保皇党":
            for i in range(len(KillTheKing.players)):
                cur_score = 0
                if KillTheKing.character[i]["name"] in ["国王", "守卫"]:
                    cur_score += 1
                    if KillTheKing.character[i]['show'] != '暗牌':
                        cur_score += 1
                score_this_round.append(cur_score)
        else:
            for i in range(len(KillTheKing.players)):
                cur_score = 0
                if KillTheKing.character[i]["name"] in ["刺客", "奴隶"]:
                    cur_score += 1
                    if KillTheKing.character[i]['show'] != '暗牌':
                        cur_score += 1
                score_this_round.append(cur_score)
        board = "积分："
        for i in range(len(KillTheKing.players)):
            board += f"\n{KillTheKing.players[i].name}({KillTheKing.character[i]['name']}): {KillTheKing.score[i]} + " \
                     f"{score_this_round[i]} = {KillTheKing.score[i] + score_this_round[i]}"
            KillTheKing.score[i] += score_this_round[i]
        await ctx.send(f"第{KillTheKing.round}回合游戏结束！{team}胜利！")
        await ctx.send(board)
        if KillTheKing.round == 5:
            final_board = "游戏结束！排名："
            for i in range(len(KillTheKing.players)):
                final_board += f"\n第{i+1}名："
                maxj = [0]
                for j in range(1, len(KillTheKing.score)):
                    if KillTheKing.score[j] > KillTheKing.score[maxj[0]]:
                        maxj = [j]
                    elif KillTheKing.score[j] == KillTheKing.score[maxj[0]]:
                        maxj.append(j)
                for j in range(len(maxj)):
                    final_board += f"\n{KillTheKing.players[j].name}, 分数：{KillTheKing.score[j]}"

            await ctx.send(final_board)

        KillTheKing.round += 1
        KillTheKing.cannot_exchange = -1
        KillTheKing.waiting_action = False
        KillTheKing.king_win = None
        KillTheKing.character = []
        await self.game_setup(ctx)




    @commands.command()
    async def start(self, ctx):
        if KillTheKing.started:
            return 0
        if len(Main.players) < int(detail["min"]) or len(Main.players) > int(detail["max"]):
            await ctx.send("人数不符合游戏要求!")
            return 0
        players = Main.players
        np.random.shuffle(players)
        KillTheKing.players = players
        for i in range(len(players)):
            KillTheKing.score.append(0)
        KillTheKing.started = True
        await self.game_setup(ctx)

    async def game_setup(self, ctx):
        configs = detail["config"]
        config = configs[str(len(KillTheKing.players))]
        main_c = ["国王", "守卫", "刺客", "奴隶"]
        for i in range(len(main_c)):
            for j in range(config[i]):
                KillTheKing.character.append({"name": main_c[i], "show":"暗牌", "state":"无"})
        other = ["奴隶贩子",'肚皮舞娘','大官','占卜师']
        np.random.shuffle(other)
        for i in range(config[4]):
            KillTheKing.character.append({"name": other[i], "show":"暗牌", "state":"无"})
        np.random.shuffle(KillTheKing.character)
        KillTheKing.now = self.next(KillTheKing.now)
        await ctx.send(f"第{KillTheKing.round}回合游戏开始！")
        for i in range(len(KillTheKing.players)):
            await KillTheKing.players[i].send(f"你手上的牌是{KillTheKing.character[i]['name']}")
        await self.main(ctx)


    async def main(self, ctx):
        if KillTheKing.waiting_action:
            return 0
        if KillTheKing.king_win == KillTheKing.now:
            await self.end(ctx, "保皇党")
            return 0
        if KillTheKing.character[KillTheKing.now - 1]["state"] in ['拘留', '捕抓', '疲劳']:
            await ctx.send(f"轮到了{KillTheKing.now}号位玩家{KillTheKing.players[KillTheKing.now - 1].name}行动，其已"
                           f"被{KillTheKing.character[KillTheKing.now - 1]['state']}，自动跳过回合")
            if KillTheKing.character[KillTheKing.now - 1]["state"] in ['拘留', '疲劳']:
                KillTheKing.character[KillTheKing.now - 1]["state"] = '无'
            KillTheKing.now = self.next(KillTheKing.now)
            await self.main(ctx)
            return 0

        await self.show_embed(ctx)
        KillTheKing.waiting_action = True

    @commands.command()
    async def king(self, ctx):
        KillTheKing.waiting_action = False
        king_num = -1
        is_king = True
        for i in range(len(KillTheKing.players)):
            if KillTheKing.character[i]["name"] == "国王":
                king_num = i
                break
        if KillTheKing.players[king_num] != ctx.message.author:
            await ctx.send("你不是国王！")
            KillTheKing.waiting_action = True
            is_king = False
        if is_king and KillTheKing.king_win != None:
            await ctx.send("你已经宣示过主权了！")
        elif is_king:
            KillTheKing.king_win = KillTheKing.now
            KillTheKing.character[king_num]['show'] = '国王'
            await ctx.send("国王宣示主权！")
            await self.show_embed(ctx)
        if is_king:
            await ctx.send(f"当下次轮到{KillTheKing.players[KillTheKing.now - 1].name}行动时，如果国王尚未隐藏身份或"
                           f"死亡，则保皇党胜利！")
        KillTheKing.waiting_action = True


    @commands.command()
    async def action(self, ctx, name=None):
        if not KillTheKing.started:
            return 0
        if not KillTheKing.waiting_action:
            await ctx.send("还不能行动！")
            return 0
        if ctx.message.author != KillTheKing.players[KillTheKing.now - 1]:
            await ctx.send(f"还没轮到你哟~请{KillTheKing.players[KillTheKing.now - 1].name}行动")
        if not name:
            await ctx.send("请输入完整格式：'-action [行动]'\n例：'-action 查看'\n")
            return 0

        target_list = []
        target_str = ""
        is_end = False
        KillTheKing.waiting_action = False

        character = KillTheKing.character[KillTheKing.now - 1]["name"]

        if name == "查看":
            title=">>查看<<"
            description="可任选其他一名玩家，秘密查看该玩家的角色卡内容，但不能查看公共区域的角色卡，请回复你想要查看的玩家的座位号。"
            for i in range(len(KillTheKing.players)):
                if KillTheKing.character[i]['show'] == "暗牌" and KillTheKing.now != i + 1 \
                        and KillTheKing.character[i]["state"] != "死亡":
                    target_str += str(i + 1) + " "
                    target_list.append(str(i + 1))

        elif name == "交换" and KillTheKing.character[KillTheKing.now-1]["show"] == "暗牌":
            title=">>暗牌交换<<"
            description="你可以选择其他玩家的暗牌，与其交换角色卡，交换后双方可以重新确认新获得的角色卡内容。你也可以与中央区域的角色卡进行交" \
                        "换。你不能与先前刚与自己交换角色卡的人交换角色卡，也不能交换正在拘留状态的角色卡。请回复你想要交换的角色牌的座位号。"
            for i in range(len(KillTheKing.character)):
                if KillTheKing.character[i]["show"] == "暗牌" and i != KillTheKing.cannot_exchange \
                        and KillTheKing.character[i]["state"] != '拘留' and KillTheKing.now != i + 1 \
                        and KillTheKing.character[i]["state"] != "死亡":
                    target_list.append(str(i + 1))
                    target_str += str(i + 1) + " "

        elif name == "交换" and KillTheKing.character[KillTheKing.now-1]["show"] != "暗牌":
            title=">>明牌交换<<"
            description="你可以将自己的身份牌转为暗牌，并与其他任何暗牌进行交换。你可以选择公共区域的暗牌，也可以选择和自己交换（即保持原状）。你和被" \
                        "你交换角色牌的玩家都可以确认自己的新角色卡内容。你不能与先前刚与自己交换角色卡的人交换角色卡，也不能交换正在拘留状态" \
                        "的角色卡。请回复你想要交换角色牌的座位号，或者回复自己的座位号表示不交换，保持原样。"
            for i in range(len(KillTheKing.character)):
                if KillTheKing.character[i]["show"] == "暗牌" and i != KillTheKing.cannot_exchange \
                        and KillTheKing.character[i]["state"] != '拘留' and KillTheKing.character[i]["state"] != "死亡":
                    target_str += str(i + 1) + " "
                    target_list.append(str(i + 1))

        elif name == "技能":
            if character == "国王":
                title = ">>技能-处决<<"
                description = "你可以杀掉一个公开的'刺客'或者'奴隶'。与此同时你将'宣示主权'，当再轮到你行动时，你未曾隐藏身份或死亡，则保皇" \
                              "党胜利。请回复你想要处决的玩家的座位号"
                for i in range(len(KillTheKing.players)):
                    if KillTheKing.character[i]["state"] =='死亡':
                        continue
                    if KillTheKing.character[i]["show"] == "刺客" or KillTheKing.character[i]["show"] == "奴隶":
                        target_str += str(i + 1) + " "
                        target_list.append(str(i + 1))
            if character == "守卫":
                title = ">>技能-拘留<<"
                description = "可指定拘留其他任意玩家，如果对方没有发动'禁止拘留'技能，则其状态变为'拘留'，该玩家需暂停一个回合。请回复你想" \
                              "要拘留的玩家的座位号"
                for i in range(len(KillTheKing.players)):
                    if i == KillTheKing.now - 1 or KillTheKing.character[i]["state"] == "死亡":
                        continue
                    target_str += str(i+1) + " "
                    target_list.append(str(i+1))
            if character == "刺客":
                title = ">>技能-行刺<<"
                description = "可杀掉其他任意一名玩家，行刺时如有守卫在刺客或行刺对象邻位，可让刺客行刺失败，并将刺客杀害。请回复你想要行刺" \
                              "的玩家的座位号"
                for i in range(len(KillTheKing.players)):
                    if i == KillTheKing.now - 1 or KillTheKing.character[i]["state"] == "死亡":
                        continue
                    target_str += str(i + 1) + " "
                    target_list.append(str(i+1))
            if character == "奴隶":
                title = ">>技能-登高一呼<<"
                description = "公开身份，宣告进行革命。"
                target_str = str(KillTheKing.now)
                target_list.append(str(KillTheKing.now))
            if character == "奴隶贩子":
                title = "捕抓奴隶"
                description = "选择任意一名公开奴隶，或者其他任何隐藏的玩家。如果你选择公开奴隶，则其状态变为'捕抓'，并且直到你隐藏身份或者" \
                              "被杀害以前跳过所有行动回合。如果你选择隐藏的玩家，若其角色为'奴隶'，则他公开身份，状态变为‘捕抓’，并且你可以" \
                              "额外进行一个回合。若其角色不为奴隶，则他无需公开身份，你的行动立即结束。请回复你想要捕抓的玩家的座位号。"
                for i in range(len(KillTheKing.players)):
                    if KillTheKing.character[i]["state"] == "死亡":
                        continue
                    if KillTheKing.character[i]["show"] == "奴隶" or KillTheKing.character[i]["show"] == "暗牌":
                        target_str += str(i + 1) + " "
                        target_list.append(str(i+1))
            if character == "肚皮舞娘":
                title = "无可用技能"
                description = "你没有可用的技能，请回复'cancel'以后重新到公频决定你的行动。"
                target_str = "无可选对象"
                target_list = []
            if character == "大官":
                title = ">>技能-操弄<<"
                description = "指定一个你想要支持的阵营（1：保皇党，2：革命党），接着指定任何自由隐藏角色卡的玩家，强制其公开身份并执行技能" \
                              "。随后，该玩家状态变为‘疲劳’，需暂停一回合。如果你选择发动技能，请回复1或2选择支持阵营。"
                for i in range(len(KillTheKing.players)):
                    if KillTheKing.character[i]["state"] == "死亡":
                        continue
                    if KillTheKing.character[i]["show"] == "暗牌" and KillTheKing.character[i]["state"] == "无":
                        target_str += str(i + 1) + " "
                        target_list.append(str(i+1))
            if character == "占卜师":
                title = ">>技能-预言<<"
                description = "调查3个隐藏角色的身份牌，并预测获胜阵营。如果这一轮游戏结束且你对获胜阵营猜测成功，则你同时获胜。下一轮行动时" \
                              "，你必须执行交换行动，并且预言失效。若你被拘留导致无法交换身份牌，则预言持续有效，直到你成功交换身份牌。如果" \
                              "场上不足3个隐藏角色，那你可查看所有隐藏玩家的身份牌，但无论如何你不能看中央区域的身份牌。请回复一个你想要查看" \
                              "的玩家的座位号"
                for i in range(len(KillTheKing.players)):
                    if KillTheKing.character[i]["state"] == "死亡" or KillTheKing.character[i]["show"] != "暗牌":
                        continue
                    if KillTheKing.now == i + 1:
                        continue
                    target_str += str(i + 1) + " "
                    target_list.append(str(i+1))

        else:
            await ctx.send("请在'查看'、'交换'、'技能'三者中选择。")
            return 0

        embed = discord.Embed(title=title, description=description)

        for i in range(len(KillTheKing.players)):
            val = f"玩家：{KillTheKing.players[i].name}\n手牌：{KillTheKing.character[i]['show']}\n状态：" \
                  f"{KillTheKing.character[i]['state']}"
            embed.add_field(name=f"{str(i + 1)}号位{jdata['emoji'][i+1]}", value=val, inline=True)

        embed.add_field(name=f"{str(len(KillTheKing.players) + 1)}号位{jdata['emoji'][len(KillTheKing.players) + 1]}",
                        value="（公共区域）\n暗牌", inline=True)
        if target_str == "":
            target_str = "无可选目标"

        embed.add_field(name="可选目标", value=target_str)
        embed.set_footer(text="如果你不想使用当前行动了，请回复'cancel'，并且回到公频重新选择你的行动。")


        def check(message):
            if message.content == "cancel":
                return True
            return message.author == ctx.message.author and message.content in target_list

        await ctx.message.author.send(embed=embed)
        msg = await self.bot.wait_for("message", check=check)

        if msg.content == 'cancel':
            await ctx.message.author.send("你取消了这次行动，请回到公频重新选择新的行动。\n例：'-action 技能'")
            await ctx.send(f"{ctx.message.author.name}取消了他的行动，请重新选择行动。")
            await self.show_embed(ctx)
            KillTheKing.waiting_action = True
            return 0

        target = int(msg.content) -1

        if name == "查看":
            await ctx.message.author.send(f"你查看了{msg.content}号位的牌，他的牌是"
                                          f"{KillTheKing.character[target]['name']}")
            await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1].name}查看了{msg.content}号位的牌")

        elif name == "交换" and KillTheKing.character[KillTheKing.now-1]["show"] == "暗牌":
            self.exchange(KillTheKing.now - 1, target)
            if target == KillTheKing.now:
                KillTheKing.cannot_exchange = KillTheKing.now - 1
            await ctx.message.author.send(f"你与{msg.content}号位交换了牌，现在你的牌成为"
                                          f"{KillTheKing.character[KillTheKing.now - 1]['name']}")
            if target < len(KillTheKing.players):
                await KillTheKing.players[target].send(f"{KillTheKing.now}号位与你交换了牌，现在你的牌成为"
                                                       f"{KillTheKing.character[target]['name']}")
            await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1].name}与{msg.content}号位交换了牌")

        elif name == "交换" and KillTheKing.character[KillTheKing.now-1]["show"] != "暗牌":
            await self.close_card(ctx, KillTheKing.now - 1)
            if target == KillTheKing.now:
                KillTheKing.cannot_exchange = KillTheKing.now - 1
            if target == KillTheKing.now - 1:
                await ctx.message.author.send(f"你选择不换牌。你的牌仍为{KillTheKing.character[KillTheKing.now - 1]}，并且恢复成暗牌，")
            else:
                self.exchange(KillTheKing.now - 1, target)
                await ctx.message.author.send(f"你与{msg.content}号位交换了牌，现在你的牌成为"
                                              f"{KillTheKing.character[KillTheKing.now - 1]['name']}")
                if target < len(KillTheKing.players):
                    await KillTheKing.players[target].send(f"{KillTheKing.now}号位与你交换了牌，现在你的牌成为"
                                                                     f"{KillTheKing.character[target]['name']}")
            await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1].name}秘密地交换了牌，或者保持原样")

        elif name == "技能":
            if character == "国王":
                await self.open_card(ctx, KillTheKing.now - 1)
                KillTheKing.character[target]["state"] = '死亡'
                await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1]}是国王！他处决了{msg.content}号位玩家。")
                is_end = await self.king_win_check(ctx)
            if character == "守卫":
                await self.open_card(ctx, KillTheKing.now - 1)
                await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1].name}是守卫！他试图拘留{msg.content}号位玩家。")
                waiting = [self.next(KillTheKing.now), self.bef(KillTheKing.now)]
                dancer_success = False
                for i in waiting:
                    if KillTheKing.character[i - 1]["show"] == "肚皮舞娘" and KillTheKing.character[i - 1]["state"] != "拘留":
                        await ctx.send(f"请{KillTheKing.players[i-1].name}决定是否发动’肚皮舞‘技能，如果决定发动，请回复1，否则回复0。")
                        def dancer_check(m):
                            return m.author == KillTheKing.players[i-1] and m.content in ["1", "0"]
                        dancer_reply = await self.bot.wait_for("message", check=dancer_check)
                        if dancer_reply.content == '1':
                            await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1].name}去看"
                                           f"{KillTheKing.players[i-1].name}的肚皮舞了，拘留失败！")
                            dancer_success = True
                        break
                if not dancer_success:
                    await ctx.send(f"请{KillTheKing.players[target].name}决定是否发动’禁止拘留‘技能，这是’国王‘和’"
                                   f"守卫‘的被动技能。如果决定发动，请回复1，否则回复0。")

                    def avoid_check(m):
                        if m.author != KillTheKing.players[target]:
                            return False
                        return m.content in ['0', '1']

                    avoid_reply = await self.bot.wait_for("message", check=avoid_check)
                    if avoid_reply.content == '1':
                        if KillTheKing.character[target]["name"] != '守卫' and KillTheKing.character[target]["name"] != '国王':
                            KillTheKing.character[target]["state"] = "拘留"
                            await ctx.send("你不是’国王‘或’守卫‘！拘留成功。")
                        else:
                            await self.open_card(ctx, target)
                            await ctx.send(f"{KillTheKing.players[target].name}发动‘禁止拘留’，拘留失败了！")
                    else:
                        KillTheKing.character[target]["state"] = "拘留"
                        await ctx.send("拘留成功！")

            if character == "刺客":
                await self.open_card(ctx, KillTheKing.now - 1)
                await ctx.send(f"{KillTheKing.players[KillTheKing.now - 1]}是刺客！他试图行刺{msg.content}号位玩家。")

                waiting = [self.next(KillTheKing.now), self.bef(KillTheKing.now), self.next(target+1), self.bef(target+1)]
                final_waiting_list = []
                final_waiting_str = ""
                for i in waiting:
                    if KillTheKing.character[i-1]["state"] == '拘留':
                        continue
                    if KillTheKing.character[i-1]["show"] != '暗牌' and KillTheKing.character[i-1]["show"] != '守卫':
                        continue
                    final_waiting_list.append(KillTheKing.players[i-1])
                    final_waiting_str += KillTheKing.players[i-1].name + '，'

                await ctx.send(f"玩家{final_waiting_str}请在15秒内决定是否发动’阻止刺客‘技能，这是’守卫‘的被动技能。如果"
                                   f"决定发动，请回复1，否则请无视")

                def avoid_check(m):
                    if not m.author in final_waiting_list:
                        return False
                    if m.content == '1':
                        for i in range(len(KillTheKing.players)):
                            if KillTheKing.players[i] == m.author:
                                if KillTheKing.character[i]["name"] != '守卫':
                                    return False
                                else:
                                    return True
                try:
                    avoid_reply = await self.bot.wait_for("message", check=avoid_check, timeout=15)
                    for i in range(len(KillTheKing.players)):
                        if KillTheKing.players[i] == avoid_reply.author:
                            await self.open_card(ctx, i)
                            KillTheKing.character[KillTheKing.now - 1]["state"] = '死亡'
                            await ctx.send(f"{KillTheKing.players[i - 1].name}是守卫，行刺失败了！"
                                           f"{KillTheKing.players[KillTheKing.now - 1].name}死亡。")
                            is_end = await self.king_win_check(ctx)
                            break
                except asyncio.exceptions.TimeoutError:
                    KillTheKing.character[target]["show"] = KillTheKing.character[target]["name"]
                    KillTheKing.character[target]["state"] = "死亡"
                    await ctx.send(f"{KillTheKing.players[target].name}被刺客杀死了，他的身份是"
                                   f"{KillTheKing.character[target]['name']}")
                    if KillTheKing.character[target]['name'] == '国王':
                        await self.end(ctx, "革命党")
                        is_end = True





            if character == "奴隶":
                await ctx.send(f"{KillTheKing.players[KillTheKing.now-1].name}是奴隶！他登高一呼，所有奴隶都可以选择开牌投身革命！")
                is_end = await self.open_card(ctx, KillTheKing.now - 1)
                if is_end:
                    return 0
                await self.show_embed(ctx)

                while(True):
                    await ctx.send(f"所有玩家请在15秒内决定是否发动’投身革命‘技能，这是’奴隶‘的被动技能。如果"
                                   f"决定发动，请回复1，否则请无视")

                    def slave_check(m):
                        if m.content == '1':
                            for i in range(len(KillTheKing.players)):
                                if KillTheKing.players[i] == m.author:
                                    if KillTheKing.character[i]["name"] != '奴隶' or KillTheKing.character[i]['show'] != '暗牌':
                                        return False
                                    else:
                                        return True

                    try:
                        slave_reply = await self.bot.wait_for("message", check=slave_check, timeout=15)
                        for i in range(len(KillTheKing.players)):
                            if slave_reply.author == KillTheKing.players[i]:
                                await ctx.send(f"{KillTheKing.players[i].name}投身革命！")
                                is_end = await self.open_card(ctx, i)
                                if is_end:
                                    return 0
                                await self.show_embed(ctx, title=">>桌面<<", description="目前情况如下")
                                break
                    except asyncio.exceptions.TimeoutError:
                        await ctx.send("革命失败，游戏继续！")
                        break
        if is_end:
            return 0



        if KillTheKing.cannot_exchange != KillTheKing.now-1:
            KillTheKing.cannot_exchange = -1
        KillTheKing.now = self.next(KillTheKing.now)
        await self.main(ctx)
        return 0


def setup(bot):
    bot.add_cog(KillTheKing(bot))