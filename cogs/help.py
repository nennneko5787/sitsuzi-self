from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", brief="このBotの使い方。")
    @commands.cooldown(1, 10.0, commands.BucketType.guild)
    async def helpCommand(self, ctx: commands.Context):
        await ctx.reply("""```ansi
[2;35m[2;34m【[0m[2;35m天海㍕の[2;33mコマンド[0m[2;35m一覧[2;34m】[0m[2;35m
[2;33m[2;36mprefix[0m[2;33m -> [2;36m[2;35mrem! [2;30m[2;37mプレフィクスをつけてコマンドを実行してください
[0m[2;30m[0m[2;35m
[2;30m-= AIと会話する機能 =-[0m[2;35m
[2;36mex[0m[2;35m <[2;31mtrue[0m[2;35m/[2;35m[2;34mfalse[0m[2;35m[0m[2;35m> [2;37m[0;37mExモードを設定します。[0m[2;37m
[2;36mchara [2;35m[<[2;33mstring[0m[2;35m>] [0m[2;36m[0m[2;37m[0m[2;35m[0m[2;36m[0m[2;33m[0m[2;35m[0m[2;37mキャラクターの特徴を設定します。何も指定しなかった場合特徴を設定しません。
[2;36mcharaAppend [2;35m[<[2;33mstring[0m[2;35m>][0m[2;36m[0m[2;37m[0m[2;37m キャラクターの特徴を付け足します。
[2;36mreset [0m[2;37m[0m[2;37m会話履歴をリセットします。
【使い方】このボットにメンションまたはリプライする
[2;30m
-= (aa-bot限定)1day-chatの統計 =-
[2;35m[2;33m[2;36m[2;35mtheme [0m[2;36m[0m[2;33m[0m[2;35m[2;33mLiteral[0m[2;35m[[0m[2;30m[0m[2;37m[2;35m[2;33m"ダーク"[2;35m,[0m[2;33m "ライト"[0m[2;35m] = [2;33m"ダーク"[0m[2;35m[0m[2;37m[0m
[2;36m[2;35mtop [0m[2;36m[0m[2;35m[2;33mRange[0m[2;35m[[2;33mint[0m[2;35m, [2;33m1[0m[2;35m][0m[2;35m = [2;33m5[0m[2;35m[0m

[2;36m[2;34moneday [0m[2;36mcoinrank [2;35mtheme [0m[2;36m[2;35mtop [0m[2;36m[0m[2;37m今までのコインロール取得回数のランキング。
[2;36m[2;34moneday [0m[2;36mspdrank [0m[2;37m[2;35mtheme [0m[2;37m[2;35mtop [0m[2;37m[0m[2;37m今までのコインロール取得速度のランキング。[0m
[2;37m[2;36m[2;34moneday [0m[2;36mlaterank [2;35mtheme [0m[2;36m[2;35mtop [0m[2;36m[0m[2;37m[2;37m今までのコインロール遅刻ポイントのランキング。
[2;36m[2;34moneday [0m[2;36mgayrank [2;35mtheme [0m[2;36m[2;35mtop [0m[2;36m[0m[2;37m[2;37m今までゲイロールが付与されたランキング。[0m[2;37m[0m[2;37m[0m

```""")


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
