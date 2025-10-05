TOKEN = "MTQyNDIxMzc5Njc1ODQ5MTI5OQ.Gfo1YE.jI-Ghc3q9nya-u7dmdGvKd_hHbn3MaZqllU29Y"
import discord
from discord.ext import commands, tasks
import asyncio

# ====== PODESI OVDE ======
TOKEN = "MTQyNDIxMzc5Njc1ODQ5MTI5OQ.Gfo1YE.jI-Ghc3q9nya-u7dmdGvKd_hHbn3MaZqllU29Y"
PREFIX = "!"
WELCOME_CHANNEL = "welcome"    # ime text kanala gde ide welcome poruka (promeni ako treba)
AUTO_ROLE_NAME = "Member"      # ime role koju bot dodeljuje novim članovima
STATUS_INTERVAL = 30           # koliko često (u sekundama) da se update-uje status
# ==========================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Bot je online kao {bot.user} (ID: {bot.user.id})")
    print(f"Na {len(bot.guilds)} servera.")
    if not update_status.is_running():
        update_status.start()

# loop koji menja status (presence) — prikazuje broj članova (suma članova svih servera)
@tasks.loop(seconds=STATUS_INTERVAL)
async def update_status():
    total = sum(g.member_count for g in bot.guilds)
    await bot.change_presence(activity=discord.Game(name=f"Gleda ({total}) → Members"))

# Autorole i welcome poruka
@bot.event
async def on_member_join(member):
    # dodeli rolu (ako postoji)
    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        try:
            await member.add_roles(role)
        except Exception as e:
            print(f"Greška pri dodeljivanju role: {e}")

    # pošalji welcome poruku (ako postoji kanal sa imenom WELCOME_CHANNEL)
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL)
    if channel:
        await channel.send(f"Dobrodošao/la {member.mention}! 🎉")
    else:
        # fallback: ako nema takvog kanala, pokuša sistemski kanal
        if member.guild.system_channel:
            await member.guild.system_channel.send(f"Dobrodošao/la {member.mention}! 🎉")

# Komande
@bot.command()
async def members(ctx):
    """Prikazuje broj članova servera."""
    await ctx.send(f"Server ima **{ctx.guild.member_count}** članova.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Briše <amount> poruka (potrebna prava Manage Messages)."""
    if amount <= 0:
        await ctx.send("Unesi broj veći od 0.")
        return
    # purge obriše poruke; uključujemo i poruku komande
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Obrisano {max(0, len(deleted)-1)} poruka.")
    await asyncio.sleep(5)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    """Izbaci člana (treba pravo Kick Members)."""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member} je izbačen. Razlog: {reason}")
    except Exception as e:
        await ctx.send(f"Ne mogu izbaciti {member}. ({e})")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    """Banuje člana (treba pravo Ban Members)."""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member} je banovan. Razlog: {reason}")
    except Exception as e:
        await ctx.send(f"Ne mogu banovati {member}. ({e})")

# Jednostavan help
@bot.command()
async def help(ctx):
    txt = f"""
**Komande ({PREFIX}):**
{PREFIX}members — broj članova
{PREFIX}clear <br> — obriši poruke (Manage Messages)
{PREFIX}kick @user [razlog] — izbaci (Kick Members)
{PREFIX}ban @user [razlog] — ban (Ban Members)
"""
    await ctx.send(txt)

# Greške za komande (MissingPermissions, BadArgument...)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nemaš dovoljno prava za ovu komandu.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nedostaje argument. Proveri sintaksu komande.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Ne mogu naći tog člana. Pokušaj sa @mention-om.")
    else:
        # za debug: print greške u konzolu
        print(f"Command error: {error}")

# Start bota
bot.run("MTQyNDIxMzc5Njc1ODQ5MTI5OQ.Gfo1YE.jI-Ghc3q9nya-u7dmdGvKd_hHbn3MaZqllU29Y")



