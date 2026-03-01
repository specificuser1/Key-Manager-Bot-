import discord
from discord.ext import commands
from discord.ui import View, Button
import json
import os
import asyncio
from dashboard import run_dashboard
import os

# ---------- LOAD CONFIG ----------
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found! Set it in Railway Variables.")
ROLE_ID = so.getenv["ROLE_ID"]
ADMIN_IDS = so.getenv["ADMIN_IDS"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- FILE SETUP ----------
os.makedirs("data", exist_ok=True)

def load_keys():
    if not os.path.exists("data/keys.txt"):
        open("data/keys.txt", "w").close()
    with open("data/keys.txt") as f:
        return f.read().splitlines()

def save_keys(keys):
    with open("data/keys.txt", "w") as f:
        f.write("\n".join(keys))

def add_used(key, user):
    with open("data/used.txt", "a") as f:
        f.write(f"{key} - Redeemed by {user}\n")

# ---------- ROLE CHECK ----------
def has_access(member):
    return any(role.id == ROLE_ID for role in member.roles)

# ---------- PANEL VIEW ----------
class KeyPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

        # Dashboard Link Button
        dashboard_button = discord.ui.Button(
            label="Dashboard",
            style=discord.ButtonStyle.link,
            url="https://your-railway-url.up.railway.app"
        )

        self.add_item(dashboard_button)

    @discord.ui.button(label="Get Key", style=discord.ButtonStyle.success)
    async def get_key(self, interaction: discord.Interaction, button: Button):
        if not has_access(interaction.user):
            return await interaction.response.send_message("No Access", ephemeral=True)

        keys = load_keys()
        if not keys:
            return await interaction.response.send_message("No keys in stock!", ephemeral=True)

        key = keys.pop(0)
        save_keys(keys)
        add_used(key, interaction.user)

        await interaction.response.send_message(f"Your Key: `{key}`", ephemeral=True)

    @discord.ui.button(label="Add New Key", style=discord.ButtonStyle.primary)
    async def add_key(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in ADMIN_IDS:
            return await interaction.response.send_message("Admin Only", ephemeral=True)

        await interaction.response.send_message("Send keys line by line.", ephemeral=True)

        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
            new_keys = msg.content.splitlines()
            keys = load_keys()
            keys.extend(new_keys)
            save_keys(keys)
            await interaction.followup.send("Keys Added Successfully!", ephemeral=True)
        except:
            await interaction.followup.send("Timeout!", ephemeral=True)

    @discord.ui.button(label="Check Stock", style=discord.ButtonStyle.secondary)
    async def stock(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"Stock: {len(load_keys())} keys", ephemeral=True)

    @discord.ui.button(label="Show Admins", style=discord.ButtonStyle.danger)
    async def admins(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"Admins: {ADMIN_IDS}", ephemeral=True)

    @discord.ui.button(label="Status", style=discord.ButtonStyle.secondary)
    async def status(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Bot: Online\nDashboard: Running", ephemeral=True)

# ---------- PREFIX COMMAND ----------
@bot.command()
async def keypanel(ctx):
    embed = discord.Embed(
        title="🔑Key Manager",
        description="Use buttons below",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, view=KeyPanel())

@bot.event
async def on_ready():
    bot.add_view(KeyPanel())
    print(f"Logged in as {bot.user}")

    # Start Dashboard
    asyncio.create_task(run_dashboard())

bot.run(TOKEN)
