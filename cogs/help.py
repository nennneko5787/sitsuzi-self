# ヘルプコマンドには興味がなかったのでChatGPTを使用しました

from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", brief="このBotの使い方。")
    async def helpCommand(self, ctx: commands.Context, option: str = None):
        # ===============================
        # option あり → 詳細ヘルプ表示
        # ===============================
        if option:
            command = self.bot.all_commands.get(option)
            if not command:
                await ctx.message.reply(f"❌ コマンド `{option}` は見つかりませんでした。")
                return

            # 通常コマンドの詳細情報
            if isinstance(command, commands.Command) and not isinstance(
                command, commands.Group
            ):
                brief = command.brief or "説明なし"
                desc = command.help or "詳細説明はありません。"
                signature = command.signature or "引数なし"

                help_text = (
                    f"```\n"
                    f"{command.name} {brief}\n"
                    f"{'-' * (len(command.name) + 1 + len(brief))}\n"
                    f"{desc}\n"
                    f"使用法: rin!{command.name} {signature}\n"
                    f"```"
                )

            # グループコマンドの場合（サブコマンド一覧）
            elif isinstance(command, commands.Group):
                subcommands = command.commands
                if not subcommands:
                    help_text = f"```\n{command.name}: サブコマンドはありません。\n```"
                else:
                    max_len = max(len(c.name) for c in subcommands)
                    help_text = f"```\n{command.name} のサブコマンド一覧:\n"
                    for sub in subcommands:
                        help_text += (
                            f"  {sub.name.ljust(max_len)}  {sub.brief or '説明なし'}\n"
                        )
                    help_text += "```"

            await ctx.message.reply(help_text)
            return

        # ===============================
        # option なし → 全コマンド一覧表示
        # ===============================
        helpCommand = "```\n"

        all_commands = list(self.bot.all_commands.values())
        if not all_commands:
            await ctx.message.reply("コマンドがありません")
            return

        max_len = max(len(c.name) for c in all_commands)

        # コグごとに出力
        for cogName, cog in self.bot.cogs.items():
            commands_in_cog = [
                (c.name, c.brief or "No description")
                for c in cog.get_commands()
                if not c.hidden
            ]
            if not commands_in_cog:
                continue

            helpCommand += f"{cogName}:\n"
            for name, desc in commands_in_cog:
                helpCommand += f"  {name.ljust(max_len)}  {desc}\n"
            helpCommand += "\n"

        # No Category（コグに属さないコマンド）
        no_category_commands = [
            (c.name, c.brief or "No description")
            for c in self.bot.all_commands.values()
            if c.cog_name is None and not c.hidden
        ]
        if no_category_commands:
            helpCommand += "No Category:\n"
            for name, desc in no_category_commands:
                helpCommand += f"  {name.ljust(max_len)}  {desc}\n"
            helpCommand += "\n"

        helpCommand += "```"

        await ctx.message.reply(helpCommand)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
