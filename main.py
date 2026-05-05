import discord
from discord import app_commands
from discord.ext import commands
import os
import json

# --- DATABASE MANAGEMENT ---
DATA_FILE = "server_settings.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- DYNAMIC PREFIX LOGIC ---
def get_prefix(bot, message):
    data = load_data()
    # Returns the custom prefix if set, otherwise defaults to '!'
    return data.get(str(message.guild.id), {}).get("prefix", "!")

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents)
    
    async def setup_hook(self):
        await self.tree.sync()
        print("--- SYSTEM ONLINE: Slash Commands & Prefix Module Loaded ---")

bot = MyBot()

# REPLACE WITH YOUR ID
MY_ID = 1424069313341554879

# --- THE /SETUP MODULE (REAMPED) ---
@bot.tree.command(name="setup", description="Configure bot modules (Owner/Authorized Only)")
@app_commands.describe(
    module="Choose: prefix, welcome, or authorize", 
    setting="The new prefix, channel mention, or user mention"
)
async def setup(interaction: discord.Interaction, module: str, setting: str):
    data = load_data()
    server_id = str(interaction.guild.id)
    
    # Permission Checks
    authorized_users = data.get(server_id, {}).get("authorized", [])
    is_owner = interaction.user.id == interaction.guild.owner_id
    is_authorized = interaction.user.id in authorized_users

    if not (is_owner or is_authorized):
        await interaction.response.send_message("❌ Access Denied: Only the Server Owner or Authorized Users can use this.", ephemeral=True)
        return

    if server_id not in data:
        data[server_id] = {"prefix": "!", "welcome_channel": None, "authorized": []}

    module_choice = module.lower()

    # 1. PREFIX MODULE
    if module_choice == "prefix":
        data[server_id]["prefix"] = setting
        msg = f"✅ Server prefix has been changed to: `{setting}`"

    # 2. WELCOME MODULE
    elif module_choice == "welcome":
        chan_id = setting.replace("<#", "").replace(">", "")
        data[server_id]["welcome_channel"] = int(chan_id)
        msg = f"✅ Welcome messages set to <#{chan_id}>"
    
    # 3. AUTHORIZE MODULE
    elif module_choice == "authorize":
        user_id = int(setting.replace("<@", "").replace("!", "").replace(">", ""))
        if user_id not in data[server_id]["authorized"]:
            data[server_id]["authorized"].append(user_id)
            msg = f"✅ <@{user_id}> can now manage modules via /setup."
        else:
            msg = "User is already authorized."

    else:
        msg = "❌ Invalid module! Options: `prefix`, `welcome`, `authorize`."

    save_data(data)
    await interaction.response.send_message(msg)

# --- REAMAINING DYNO MODULES ---
@bot.event
async def on_member_join(member):
    data = load_data()
    chan_id = data.get(str(member.guild.id), {}).get("welcome_channel")
    if chan_id:
        channel = bot.get_channel(chan_id)
        if channel:
            embed = discord.Embed(title="Welcome!", description=f"Glad to have you here, {member.mention}!", color=discord.Color.green())
            await channel.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🛰️ Latency: `{round(bot.latency * 1000)}ms`")

@bot.tree.command(name="globalping", description="Broadcast to everyone (Bot Owner Only)")
async def globalping(interaction: discord.Interaction):
    if interaction.user.id == MY_ID:
        await interaction.response.send_message("@everyone **GLOBAL BROADCAST** 🚨")
    else:
        await interaction.response.send_message("❌ Unauthorized.", ephemeral=True)

# --- START ---
token = os.getenv('DISCORD_TOKEN')
bot.run(token)