import asyncio
import discord
from discord.ext import commands
from game import Player, Game
from utils import new_elo_rating
from utils.database import RocketStats


class Confirm(discord.ui.View):
    """Confirmation buttons"""

    def __init__(self, user):
        super().__init__()
        self.value = None
        self.user = user

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):

        self.value = True
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.value = False
        self.stop()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user == self.user:
            return True
        await interaction.response.send_message("That's not for you!", ephemeral=True)
        return False


class Battle(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.bosses = [
            #   (Name, maxlvl, +xp, +money, Stats)
            ("Axel", 3, 10, 250, RocketStats(1, 125, 25, 300, 5)),
            ("Cronos", 5, 25, 500, RocketStats(3, 150, 30, 350, 7)),
            ("Demos", 7, 50, 1000, RocketStats(5, 175, 50, 400, 10)),
            ("Eros", 10, 100, 2000, RocketStats(10, 200, 60, 500, 15)),
            ("Ultimate Bob", 100, 696969, 100, RocketStats(0, 1000, 500, 1000, 69)),
        ]

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Meh
        await ctx.reply(str(error))
        raise error

    @commands.command()
    @commands.cooldown(1, 25, commands.BucketType.user)
    async def challenge(self, ctx, user: discord.Member, bet: int = 10):
        if user == ctx.author:
            return await ctx.send("You can't challenge yourself!")
        elif user.bot:
            return await ctx.send(
                "You can't challenge bots! Though I'm sure they'd beat you"
            )

        if not 0 < bet < 101:
            return await ctx.send("Bet must be between 1-100 coins.")

        p1user_data = await self.bot.db.fetch_user(ctx.author)
        p2user_data = await self.bot.db.fetch_user(user)

        if p1user_data.money < bet:
            return await ctx.send("You don't have enough money to challenge them!")
        if p2user_data.money < bet:
            return await ctx.send(
                "They don't have enough money to accept the challenge!"
            )

        p1rocket = await self.bot.db.fetch_rocket(ctx.author)
        p2rocket = await self.bot.db.fetch_rocket(user)

        p1, p2 = Player(*p1rocket.game_data), Player(*p2rocket.game_data)
        game = Game(p1, p2)
        render_task = asyncio.ensure_future(self.bot.run_async(game.run))

        embed = discord.Embed(
            title=f"Challenge from: {ctx.author.name} [Elo: {p1user_data.elo} | XP: {p1user_data.xp}]",
            description=f"You'll have to pay {bet} duckcoins if you lose. But if you win you'll get {bet+round(bet/10)} duckcoins!",
            color=discord.Color.red(),
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/682157382062964781/919430883977592843/unknown.png"
        )

        view = Confirm(user)
        og_msg = await ctx.reply(user.mention, embed=embed, view=view)

        await view.wait()
        await og_msg.delete()
        if not view.value:
            render_task.cancel()
            return await ctx.reply(
                f"{user.name} has declined your challenge. What a coward!"
            )

        embed = discord.Embed(
            title=f"Let the race begin!",
            description="Rendering the game...",
            color=discord.Color.red(),
        )
        embed.add_field(name="White Duck", value=ctx.author.name)
        embed.add_field(name="Yellow Duck", value=user.name)
        embed.set_image(
            url="https://media.discordapp.net/attachments/682157382062964781/919430883977592843/unknown.png"
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/822084080211722330.gif?size=160"
        )
        m = await ctx.reply(embed=embed)

        while not render_task.done():
            await asyncio.sleep(0.1)
        image_bytes = render_task.result()
        embed = discord.Embed(
            title=f"{ctx.author.name} vs {user.name}!",
            description=f"The loser pays the winner {bet} duckcoins!",
            color=discord.Color.red(),
        )
        embed.add_field(name="White Duck", value=ctx.author.name)
        embed.add_field(name="Yellow Duck", value=user.name)
        embed.set_image(url="attachment://ducc.gif")
        score = {None: 0.5, "White": 1, "Yellow": 0}
        statement = {
            None: "It's a tie!",
            "White": f"{ctx.author.name} wins!",
            "Yellow": f"{user.name} wins!",
        }
        p1elo, p2elo = new_elo_rating(
            p1user_data.elo, p2user_data.elo, score[game.winner]
        )
        await self.bot.db.update_elo_rating(ctx.author, p1elo - p1user_data.elo)
        await self.bot.db.update_elo_rating(user, p2elo - p2user_data.elo)
        await m.edit(embed=embed, file=discord.File(image_bytes, filename="ducc.gif"))
        if game.winner:
            winner = ctx.author if game.winner == "White" else user
            loser = ctx.author if winner == user else user
            await self.bot.db.update_money(winner, bet + round(bet / 10))
            await self.bot.db.update_money(loser, -bet)

        await asyncio.sleep(8)
        await m.edit(
            content=f"|| {statement[game.winner]} | New Elo Ratings {ctx.author.name}={p1elo}, {user.name}={p2elo}||",
        )

    @commands.group(aliases=["bosses"], invoke_without_command=True)
    async def boss(self, ctx):
        embed = discord.Embed(title="Bosses", color=discord.Color.random())
        for i in self.bosses:
            embed.add_field(
                name=f"{i[0]} | +{i[2]} XP | +{i[3]} {self.bot.duckcoin}",
                value=str(i[-1]),
            )
        await ctx.send(embed=embed)

    @boss.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def fight(self, ctx, name):
        boss = [x for x in self.bosses if x[0] == name.title()]
        if not boss:
            return await ctx.send("Invalid boss!")
        name, maxlvl, xp, money, bossrocket = boss[0]

        user_data = await self.bot.db.fetch_user(ctx.author)

        if user_data.money < money // 10:
            return await ctx.send(
                f"You don't have enough money to challenge this boss ({money//10} {self.bot.duckcoin})!"
            )
        if user_data.level >= maxlvl:
            return await ctx.send(
                f"You can't fight this boss since you are overleveled!"
            )

        p1rocket = await self.bot.db.fetch_rocket(ctx.author)

        p1, p2 = Player(*p1rocket.game_data), Player(*bossrocket.game_data)
        game = Game(p1, p2)
        render_task = asyncio.ensure_future(self.bot.run_async(game.run))

        embed = discord.Embed(
            title=f"Boss Battle vs {name}!",
            description="Rendering the game...",
            color=discord.Color.red(),
        )
        embed.add_field(name="White Duck", value=ctx.author.name)
        embed.add_field(name="Yellow Duck", value=name)
        embed.set_image(
            url="https://media.discordapp.net/attachments/682157382062964781/919430883977592843/unknown.png"
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/822084080211722330.gif?size=160"
        )
        m = await ctx.reply(embed=embed)

        while not render_task.done():
            await asyncio.sleep(0.1)
        image_bytes = render_task.result()
        embed = discord.Embed(
            title=f"{ctx.author.name} vs {name}!", color=discord.Color.red()
        )
        embed.add_field(name="White Duck", value=ctx.author.name)
        embed.add_field(name="Yellow Duck", value=name)
        embed.set_image(url="attachment://ducc.gif")
        statement = {
            None: "It's a tie!",
            "White": f"{ctx.author.name} wins!",
            "Yellow": f"{name} wins!",
        }
        await m.edit(embed=embed, file=discord.File(image_bytes, filename="ducc.gif"))
        if game.winner:
            prize = money if game.winner == "White" else -money // 10
            await self.bot.db.update_money(ctx.author, prize)
            if prize > 0:
                await self.bot.db.update_xp(ctx.author, xp)
            else:
                await self.bot.db.update_xp(ctx.author, bossrocket.id)

        await asyncio.sleep(8)
        await m.edit(
            content=f"|| {statement[game.winner]} ||",
        )


def setup(bot):
    bot.add_cog(Battle(bot))
