import asyncio
from contest import check, make_url
from contextlib import redirect_stdout
import discord
from discord.ext import commands
from dotenv import load_dotenv
import io
import os
import sys
from textwrap import indent
import time
from traceback import format_exception

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
async def add(ctx, *args):
    if len(args) % 2 != 0:
        await ctx.reply('invalid')
        return

    for i in range(len(args) // 2):
        aliases = args[2*i].split('|')
        year = args[2*i + 1]

        # "contest|alias1|alias2|..."
        contest = aliases[0]

        # Already checking another same year contest
        if any(c[0] == contest and c[1] == year for c in monitoring):
            return

        monitoring.append((contest, year, aliases))

    await ctx.message.add_reaction('🤓')


async def check_contests(channel: discord.TextChannel):
    global monitoring

    not_out = []
    out = []

    for contest, year, aliases in monitoring:
        is_out = False

        for alias in aliases:
            url = make_url(alias, year)

            status = check(url)

            if status == 0:
                await channel.send('@everyone {} {} RESULTS ARE OUT!!!\n\n[Results]({})\n\n[CEMC website](https://www.cemc.uwaterloo.ca/contests/past_contests.html)\n--------'.format(contest, year, url))

                out.append((contest, year, aliases))
                is_out = True
                break
            elif status == -1:
                await channel.send('something went wrong ({} {} {})'.format(contest, alias, year))

        # All aliases of the contest are not out
        if not is_out:
            not_out.append((contest, year, aliases))

    if len(not_out) > 0:
        contests = ', '.join(contest + ' ' + year for contest, year, _ in not_out)
        await channel.send(contests + ' results are not out')

    monitoring = [x for x in monitoring if x not in out]


async def loop(channel: discord.TextChannel, interval: int):
    global looping

    if looping:
        await channel.send('already looping')
        return

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


@bot.command(name='alive')
async def alive(ctx):
    await ctx.reply('alive ({}ms)'.format(round(bot.latency * 1000)))


@bot.command(name='exec')
@perms_only()
async def exec_command(ctx, *, code):
    globals = {
        'discord': discord,
        'commands': commands,
        'bot': bot,
        'ctx': ctx,
        'start_loop': start_loop,
        'loop': loop,
        'add': add,
        'check_contests': check_contests,
        'monitoring': monitoring,
        'operators': operators,
    }
    
    buffer = io.StringIO()

    try:
        with redirect_stdout(buffer):
            exec('async def func():\n{}'.format(indent(code, '    ')), globals)
            func = await globals['func']()

            await ctx.message.add_reaction('🤓')

    except Exception as e:
        time_begin = time.time()
        result = ''.join(format_exception(e, e, e.__traceback__))

        embed = discord.Embed(title='')
        embed.add_field(name='', value = ('```py\n{}```'.format(result)))
        embed.set_footer(text='evaluated in {} ms'.format(round((time.time() - time_begin) * 1000)))

        await ctx.send(embed=embed)


if __name__ == '__main__':
    token = os.getenv('TOKEN')
    bot.run(token)
