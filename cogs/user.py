from typing import Literal
import discord
from discord.ext import commands
from utils.database import User as UserStats
import random

class User(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=['bal', 'prof'])
    async def profile(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        data = await self.bot.db.fetch_user(user)

        embed = discord.Embed(title=f'{user.name}\'s Profile', color=discord.Color.random())
        embed.add_field(name='Elo rating', value=data.elo)
        embed.add_field(name=f'Level {data.level}', value=f"XP: {data.xp}")
        embed.add_field(name='Money', value=f'{data.money} {self.bot.duckcoin}')
        embed.set_thumbnail(url=user.display_avatar.url)
        await ctx.reply(embed=embed)

    @commands.command()
    async def stats(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        data = await self.bot.db.fetch_rocket(user)

        embed = discord.Embed(title=f'{user.name}\'s Duck and Rocket Stats', color=discord.Color.random())
        embed.add_field(name='Thrust Force', value=f'{data.thrust} Peta Newton')
        embed.add_field(name='Fuel Capacity', value=f'{data.fuel} Zeta liters', inline=False)
        embed.add_field(name='Max Velocity', value=f'{data.max_velocity} parsec/s')
        embed.add_field(name='Duck Intelligence', value=f'{round(data.pilot_intel, 2)}%')

        embed.set_thumbnail(url='https://media.discordapp.net/attachments/682157382062964781/919425474382430250/duck-rocket2.png')
        await ctx.reply(embed=embed)
    
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, target: Literal["elo", "money", "xp"] = "elo"):
        res = await self.bot.db.fetchall(f"SELECT * FROM user ORDER BY {target} DESC LIMIT 5")
        embed = discord.Embed(title=f"🏆 {target.title()} Leaderboard", color = discord.Color.random())        
        emoji = "points" if target == "elo" else self.bot.duckcoin if target == "money" else "xp"
        for i, r in enumerate(res):
            user = self.bot.get_user(r[0]) or await self.bot.fetch_user(r[0])
            r = UserStats(*r)
            embed.add_field(name=f'{i+1}. {user.name}',value=f"{getattr(r, target)} {emoji}", inline=False)
        await ctx.reply(embed=embed)  

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def work(self, ctx):
        user = await self.bot.db.fetch_user(ctx.author)
        earnings = random.randint(5, int(15*user.level*.6))
        await self.bot.db.update_money(ctx.author, earnings)
        work = [
            'repair spaceships', 
            'work as a technician', 
            'fix the engine', 
            'deliver inter-galactic packages',
            'study the nearby supernova'
        ]
        w = random.choice(work)
        await ctx.reply(f"You forced your duck to {w} and earned {earnings} {self.bot.duckcoin}. How cruel.")


    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def claim(self, ctx):
        """
        Claim money for your elo rating points!
        """
        user = await self.bot.db.fetch_user(ctx.author)
        earnings = int(user.elo/100)
        await self.bot.db.update_money(ctx.author, earnings)
        await ctx.reply(f"You claimed {earnings} {self.bot.duckcoin} from the Elo Leaderboard.")

def setup(bot):
    bot.add_cog(User(bot))