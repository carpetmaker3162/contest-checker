import asyncio
from contest import check, make_url
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys

load_dotenv()

operators = [672892838995820553]
bot = commands.Bot(
        command_prefix='.',
        intents=discord.Intents.all(),
        help_command=None)

monitoring = []
looping = False

def perms_only():
    def has_perms(ctx):
        return ctx.author.id in operators
    return commands.check(has_perms)

@bot.command(name='add')
@perms_only()
async def add(ctx, *contests):
    if len(contests) % 2 != 0:
        await ctx.reply('invalid')
        return

    for i in range(len(contests) // 2):
        contest = contests[2*i]
        year = contests[2*i + 1]

        if (contest, year) in monitoring:
            return

        monitoring.append((contest, year))

    await ctx.message.add_reaction('🤓')

async def check_contests(channel: discord.TextChannel):
    global monitoring

    not_out = []
    out = []

    for contest, year in monitoring:
        url = make_url(contest, year)

        status = check(url)

        if status == 1:
            not_out.append((contest, str(year)))
        elif status == 0:
            await channel.send('@everyone {} {} RESULTS ARE OUT!!!\n\n[Results]({})\n\n[CEMC website](https://www.cemc.uwaterloo.ca/contests/past_contests.html)\n--------'.format(contest, year, url))

            out.append((contest, year))
        elif status == -1:
            await channel.send('something went wrong ({} {})'.format(contest, year))

    if not_out:
        contests = ', '.join(contest + ' ' + year for contest, year in not_out)
        await channel.send(contests + ' results is/are not out')

    monitoring = [x for x in monitoring if x not in out]

async def loop(channel: discord.TextChannel, interval: int):
    global looping

    if looping:
        await ctx.reply('already looping')

    looping = True
    await bot.wait_until_ready()

    while not bot.is_closed():
        await check_contests(channel=channel)
        await asyncio.sleep(interval)

@bot.command(name='loop')
@perms_only()
async def start_loop(ctx, interval: int = 900):
    try:
        bot.loop.create_task(loop(ctx.channel, interval))
        await ctx.message.add_reaction('🤓')
    except Exception as e:
        print(e)

@bot.command(name='restart')
@perms_only()
async def restart(ctx):
    await ctx.message.add_reaction('⌛')
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
    token = os.getenv('TOKEN')
    bot.run(token)
