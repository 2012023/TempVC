import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# User defined variables
DISCORD_TOKEN = # INSERT DISCORD TOKEN HERE
join_channel = # INSERT JOIN CHANNEL ID HERE

marked_for_deletion = dict()


async def create_lobby(member):
    global marked_for_deletion

    # Generate new category
    guild = member.guild
    new_category = await guild.create_category(f"{member.name}'s private lobby", position=1)

    # Generate new channels in new category
    new_voice_channel = await new_category.create_voice_channel(f"{member.name}'s VC")
    new_text_channel = await new_category.create_text_channel(f"VC Chat")
    print(f"'{new_category}' created")

    # Append all generated channels in marked_for_deletion
    marked_for_deletion[new_category.id] = [new_category.id, new_text_channel.id, new_voice_channel.id]

    # Move user to newly created voice channel
    await member.move_to(new_voice_channel)

async def check_before_channel(before_channel):
    # Check if channel is empty, and deletes category including all channels
    if before_channel.category.id in marked_for_deletion and len(bot.get_channel(before_channel.id).members) == 0:
        marked_category = before_channel.category

        # Deletes channels in category if channels are marked for deletion
        for channel in marked_category.channels:
            if channel.id in marked_for_deletion[before_channel.category.id]:
                await channel.delete()

        # Deletes category if category is in marked_for_deletion
        await bot.get_channel(marked_category.id).delete()

        del marked_for_deletion[before_channel.category.id]

        print("Channel", before_channel.name, "deleted")


async def check_channels(member, before_channel, after_channel):
    # Checks if channel user left exists
    if before_channel is not None:
        await check_before_channel(before_channel)

    # Checks if channel user joined is join_channel
    if after_channel is not None:
        if after_channel.id == join_channel:
          print(f"{member.name} entered 'Create VC' channel")
          await create_lobby(member)


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"{member} went from {before.channel} to {after.channel}.")
    await check_channels(member, before.channel, after.channel)


@bot.event
async def on_ready():
    print('Logged in')
    print(bot.user.name)
    print(bot.user.id)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" .help doesnt work lmao"))

async def main():
    await bot.start(DISCORD_TOKEN)

asyncio.run(main())
