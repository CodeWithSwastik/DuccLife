import random 
from typing import Literal
import discord
from discord.ext import commands
from utils import calc_cost

class Upgrades(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

        self.price_map = {
            "fuel": (10, 10, 1),
            "engine": (100, 30, 5),
            "velocity": (250, 20, 10)
        }

    @commands.command()
    async def upgrades(self, ctx):
        data = await self.bot.db.fetch_rocket(ctx.author)

        embed = discord.Embed(title='Upgrades', description=f"Use {ctx.prefix}upgrade `fuel|engine|velocity` to upgrade your rocket.", color=discord.Color.random())
        embed.add_field(name="Engine", value=f"+5 Peta Newton\nCost: {calc_cost(data.thrust, *self.price_map['engine'])} {self.bot.duckcoin}", inline=False)
        embed.add_field(name="Fuel Tank", value=f"+1 Zeta liters\nCost: {calc_cost(data.fuel, *self.price_map['fuel'])} {self.bot.duckcoin}")
        embed.add_field(name="Max Velocity", value=f"+10 parsec/s\nCost: {calc_cost(data.max_velocity, *self.price_map['velocity'])} {self.bot.duckcoin}")

        embed.set_thumbnail(url='https://media.discordapp.net/attachments/682157382062964781/919485727585210388/duck-rocket1.png')
        await ctx.send(embed=embed)

    @commands.command()
    async def upgrade(self, ctx, part: Literal["fuel", "velocity", "engine"]):
        userdata = await self.bot.db.fetch_user(ctx.author)
        rocketdata = await self.bot.db.fetch_rocket(ctx.author)

        if part == "fuel":
            cost = calc_cost(rocketdata.fuel, *self.price_map[part])
        elif part == "velocity":
            cost = calc_cost(rocketdata.max_velocity, *self.price_map[part])
        else:
            cost = calc_cost(rocketdata.thrust, *self.price_map[part])

        if cost > userdata.money:
            return await ctx.send(f"You don't have {cost} {self.bot.duckcoin} to do this upgrade!")

        await self.bot.db.update_money(ctx.author, -cost)
        await self.bot.db.update_rocket(ctx.author, part, self.price_map[part][-1])
        await ctx.send(f"Your rocket has been upgraded! Use `{ctx.prefix}stats` to see the new stats!")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def train(self, ctx):
        userdata = await self.bot.db.fetch_user(ctx.author)
        if 10 > userdata.money:
            return await ctx.reply(f"You don't have 10 {self.bot.duckcoin} to buy equipment for this training session!")
        await self.bot.db.update_money(ctx.author, -10)
        if random.randrange(1, 11) > 8:
            await self.bot.db.update_intel(ctx.author, -random.randint(1, 10)/100)
            await ctx.reply(f"The training wasn't successful! Your duck seems be to be in a lot of stress.")
        else:
            await self.bot.db.update_intel(ctx.author, random.randint(1, 25)/100)
            await ctx.reply(f"The training was successful!")


def setup(bot):
    bot.add_cog(Upgrades(bot))