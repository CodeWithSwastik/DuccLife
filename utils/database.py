import aiosqlite
import discord
from discord.ext import commands
from dataclasses import dataclass

class Database:
    """
    Class for all interaction with the database.
    """

    user_db = "./db/user.db"

    def get_db_path(self, name):
        return f"./db/{name}.db"

    async def create_user_tables(self):
        async with aiosqlite.connect(self.user_db) as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user (
                    id BIGINT PRIMARY KEY NOT NULL,
                    elo INT NOT NULL,
                    xp BIGINT NOT NULL,
                    money BIGINT NOT NULL
                );
            """
            )
            await conn.commit()

        async with aiosqlite.connect(self.user_db) as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rocket (
                    id BIGINT PRIMARY KEY NOT NULL,
                    thrust INT NOT NULL,
                    fuel INT NOT NULL,
                    maxVelocity INT NOT NULL,
                    pilotIntel REAL NOT NULL
                );
            """
            )
            await conn.commit()




    async def fetch_user(self, user: discord.Member):
        """
        Get user data from database.
        """
        await self.create_user_tables()

        user_data = await self.fetchone("SELECT * FROM user WHERE id = ?", user.id)
        if user_data:
            user_data = User(*user_data)
        else:
            user_data, _ = await self.create_new_user(user)
            
        return user_data

    async def fetch_rocket(self, user: discord.Member):
        """
        Get rocket data from database.
        """
        await self.create_user_tables()

        rocket = await self.fetchone("SELECT * FROM rocket WHERE id = ?", user.id)
        if rocket:
            rocket = RocketStats(*rocket)
        else:
            _, rocket = await self.create_new_user(user)

        return rocket

    async def fetchone(self, query: str, *args, db="user"):
        async with aiosqlite.connect(self.get_db_path(db)) as conn:
            data = await conn.execute(query, args)
            return await data.fetchone()

    async def fetchall(self, query: str, *args, db="user"):
        async with aiosqlite.connect(self.get_db_path(db)) as conn:
            data = await conn.execute(query, args)
            return await data.fetchall()

    async def execute(self, query: str, *args, db="user"):
        async with aiosqlite.connect(self.get_db_path(db)) as conn:
            await conn.execute(query, args)
            return await conn.commit()

    async def create_user(self, user, rocket):
        await self.execute("""
                INSERT INTO user (id, elo, xp, money)
                VALUES (?, ?, ?, ?);
                """,
            user.id,
            user.elo,
            user.xp,
            user.money
        )
    
        await self.execute("""
                INSERT INTO rocket (id, thrust, fuel, maxVelocity, pilotIntel)
                VALUES (?, ?, ?, ?, ?);
                """,
            user.id,
            rocket.thrust,
            rocket.fuel,
            rocket.max_velocity,
            rocket.pilot_intel
        )
    
    async def create_new_user(self, member: discord.Member):
        user = User.default(member.id)
        rocket = RocketStats.default(member.id)
        await self.create_user(user, rocket)
        return user, rocket

    async def update_elo_rating(self, member: discord.Member, change: int):
        await self.execute("UPDATE user SET elo = elo + ? WHERE id = ?", change, member.id)

    async def update_money(self, member: discord.Member, change: int):
        await self.execute("UPDATE user SET money = money + ? WHERE id = ?", change, member.id)

    async def update_xp(self, member: discord.Member, change: int):
        await self.execute("UPDATE user SET xp = xp + ? WHERE id = ?", change, member.id)

    async def update_rocket(self, member: discord.Member, part: str, change: int):
        part = {
            "fuel": "fuel",
            "engine": "thrust",
            "velocity": "maxVelocity"
        }[part]

        await self.execute(f"UPDATE rocket SET {part} = {part} + ? WHERE id = ?", change, member.id)
        
    async def update_intel(self, member: discord.Member, change: float):
        await self.execute("UPDATE rocket SET pilotIntel = pilotIntel + ? WHERE id = ?", round(change, 2), member.id)
        
@dataclass
class User:
    id: int
    elo: int
    xp: int
    money: int

    @property
    def level(self) -> int:
        return round(0.51 * self.xp ** 0.5)

    @classmethod
    def default(cls, id):
        return cls(id, 400, 1, 100)

@dataclass
class RocketStats:
    id: int
    thrust: int
    fuel: int
    max_velocity: int
    pilot_intel: float

    @property
    def game_data(self):
        return (self.thrust/10000, self.fuel, self.max_velocity/100, self.pilot_intel)

    @classmethod
    def default(cls, id):
        return cls(id, 100, 10, 250, 1)

    def __str__(self):
        return f"Rocket: thrust={self.thrust} fuel={self.fuel} maxVel={self.max_velocity} intel={self.pilot_intel}"