import discord
import os
from discord.ext import commands

# 1. SETUP
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="!", intents=intents)

# REPLACE THE NUMBERS BELOW WITH YOUR ACTUAL USER ID
MY_ID = 1424069313341554879 

@bot.event
async def on_ready():
    print(f'--- SYSTEM ONLINE ---')
    print(f'Logged in as: {bot.user.name}')

# --- PING COMMAND ---
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓')

# --- GLOBAL PING (ONLY FOR YOU) ---
@bot.command()
async def globalping(ctx):
    if ctx.author.id == MY_ID:
        await ctx.send('@everyone THIS IS A GLOBAL PING! 🚨')
    else:
        await ctx.send("You are not authorized to use this command.")

# --- MUTE SYSTEM ---
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'{member.mention} has been muted. Reason: {reason}')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f'{member.mention} has been unmuted.')
    else:
        await ctx.send(f'{member.mention} is not muted.')

# Error handling
@mute.error
@unmute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to manage roles.")

# --- CONNECTION ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)