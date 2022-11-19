import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, activity=discord.Activity(type=discord.ActivityType.playing, name=" .help doesnt work lmao"))

bot.lobbies = dict()
bot.new_category = False

# User defined variables
DISCORD_TOKEN = # INSERT TOKEN HERE
join_channel = # INSERT JOIN CHANNEL ID HERE
bot.category_position = # INSERT POSITION (INT)


async def create_lobby(member):
    guild = member.guild

    # Generate new category if necessary
    if not bot.new_category:
        bot.new_category = await guild.create_category(f"private lobbies", position=bot.category_position)

    # Generate new VC with new Lobby ID
    number = min([x + 1 for x in range((len(bot.lobbies) + 1)) if x + 1 not in [bot.lobbies[x]["Lobby ID"] for x in bot.lobbies]])
    new_voice_channel = await bot.new_category.create_voice_channel(f"┗ {number} • {member.name}'s channel", bitrate=96000)
    try:
        await member.move_to(new_voice_channel)
    except Exception as e:
        print(e)
        await check_before_channel(member, new_voice_channel)

    # Generate new Text Channel
    setup_overwrite = {guild.default_role: discord.PermissionOverwrite(view_channel=False), member: discord.PermissionOverwrite(view_channel=True)}
    new_text_channel = await bot.new_category.create_text_channel(f"{member.name}s chat", overwrites=setup_overwrite)

    # Append all generated channels in bot.lobbies and buttons_dict
    bot.lobbies[new_voice_channel.id] = {"overwrites": setup_overwrite, "chat": new_text_channel, "voice": new_voice_channel, "Lobby ID": number}

    # Sets channel permissions
    await check_before_channel(member, new_voice_channel, change_permission=False)


async def check_before_channel(member, before_channel, change_permission=True):

    # Removes view_channel permission when channel is left
    if change_permission:
        if before_channel.id in bot.lobbies:
            bot.lobbies[before_channel.id]["overwrites"][member] = discord.PermissionOverwrite(view_channel=False)
            await bot.lobbies[before_channel.id]["chat"].edit(overwrites=bot.lobbies[before_channel.id]["overwrites"])

    # Check if channel is empty, if so, deletes category including all channels
    if before_channel.id in bot.lobbies and len(bot.get_channel(before_channel.id).members) == 0:
        marked_category = before_channel.category

        # Deletes channels in category if channels are marked for deletion
        await bot.lobbies[before_channel.id]["chat"].delete()
        await bot.lobbies[before_channel.id]["voice"].delete()

        # Deletes channels from bot.lobbies
        del bot.lobbies[before_channel.id]

        # Deletes category if category is empty
        if not marked_category.channels:
            await bot.get_channel(marked_category.id).delete()
            bot.new_category = False


async def check_channels(member, before_channel, after_channel):

    # Checks if channel user left exists
    if before_channel is not None:
        await check_before_channel(member, before_channel)

    if after_channel is not None:
        # Checks if user is in "Create VC" channel
        if after_channel.id == join_channel:
            await create_lobby(member)

        # Sets view-permissions when channel is joined
        if after_channel.id in bot.lobbies:
            bot.lobbies[after_channel.id]["overwrites"][member] = discord.PermissionOverwrite(view_channel=True)
            await bot.lobbies[after_channel.id]["chat"].edit(overwrites=bot.lobbies[after_channel.id]["overwrites"])


@bot.event
async def on_voice_state_update(member, before, after):
    await check_channels(member, before.channel, after.channel)


@bot.event
async def on_ready():
    print(f"{bot.user.name} logged in")


async def main():
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
