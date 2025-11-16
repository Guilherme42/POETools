# %%
import re 
import TOKENS as tk
import time

import discord as dc
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as bs
import difflib

intents = dc.Intents.default()
intents.message_content = True

class myBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(Funcs(self))

bot = myBot(command_prefix="!", intents=intents, description="Searches poewiki for [[item name]] and returns the first result.")

wikilink    = f"http://www.poewiki.net/wiki/"
searchlink  = f"http://www.poewiki.net/w/api.php"


class Funcs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # @commands.hybrid_command(name="pedro", description="Destroys Pedro")
    @commands.hybrid_command(name="pedro", description="Destroys Pedro", help="Destroys Pedro", with_app_command=True)
    async def pedro(self, ctx: commands.Context):
        pedro = await ctx.guild.fetch_member(tk.PEDRO)
        if pedro:
            await self.destroy(ctx, pedro)

    @commands.hybrid_command(name="destroy", description="Destroys other users", help="Destroys other users", with_app_command=True)
    # @commands.hybrid_command(name="destroy", description="Destroys other users")
    async def destroy(self, ctx: commands.Context, user: dc.Member):
        await ctx.send(f"Destroying {user.display_name}...")
        destroyed = False
        async for mess in ctx.channel.history(limit=100):
            if mess.author.id == user.id:
                await mess.add_reaction("💥")
                destroyed = True
                break
        if destroyed:
            await ctx.send(f"<@{user.id}> has been successfully destroyed.")
        else:
            await ctx.send(f"No {user.display_name} found to destroy. :(")
    # bot.add_command(destroy)
    # bot.tree.add_command(destroy.app_command)


@bot.event
async def on_message(ctx: dc.message.Message):
    # Prevents responding to itself.
    if ctx.author == bot.user:
        return
    
    # Check if the message contains the [[ ]] tag to search.
    pattern = r"\[\[(.*?)\]\]"
    matches = re.search(pattern, ctx.content)
    if matches:
        print(f"match: {matches}")
        print(f"possible search for {matches.group(1)}: {wikilink}{matches.group(1).replace(' ','_')}")
        await ctx.channel.send(f"{wikilink}{matches.group(1).replace(' ','_')}")

    # on_message is an existing event that is being overwritten. This is needed to ensure the other ! commands still work.
    await bot.process_commands(ctx)


@bot.tree.command(name="reload_commands", description="Reloads all bot commands." )
async def reload_commands(interaction: dc.Interaction):
    if interaction.user.id != tk.ME:
        await interaction.response.send_message("You are not authorized to use this command.")
    else:
        await bot.tree.sync()
        await interaction.response.send_message("Commands reloaded. press Ctrl+R to refresh the command list.")

@bot.tree.command(name="wiki", description="Searches poewiki for the item and returns the first result.")
async def wiki(interaction: dc.Interaction, item: str):
    # Assemble url to fetch from the wiki.
    url = f"{wikilink}{item.replace(' ','_')}"
    # await scrape_wiki_for_item_card(url)
    await interaction.response.send_message(url)

@wiki.autocomplete("item")
async def wiki_autocomplete(interaction: dc.Interaction, current: str):
    current = current.strip()
    if not current:
        return []
    titles = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            searchlink,
            params={
                "action": "query",
                "list": "search",
                "srsearch": f"intitle:{current.lower()}*",
                "srlimit": 15,
                "format": "json"
            }
        ) as resp2:
            if resp2.status == 200:
                data2 = await resp2.json()
                print(data2)
                more = [s['title'] for s in data2['query']['search'] if s['title']and not re.search(r"may refer to", s['snippet'])]
                print(more)
                titles.extend(more)
    
    print("titles:", titles)
    # return [dc.app_commands.Choice(name=s['title'], value=s['title']) for s in data1["query"]["search"]]
    rankedlist = sorted(
        titles,
        key = lambda title: difflib.SequenceMatcher(a=current.lower(), b=title.lower()).ratio(),
        reverse=True
    )
    # returns only top 5 results
    return [dc.app_commands.Choice(name=n, value=n) for n in rankedlist[:5]]

async def scrape_wiki_for_item_card(item_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(item_url) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = bs(html, 'html.parser')
                item_card = soup.find("span", class_ = lambda c: c and c.startswith("item-box"))
                # Get item title
                title = item_card.find("span", class_ = lambda c: c and c.startswith("header")).get_text(separator=" ").strip()
                # Get item stats
                stats = item_card.find("span", class_ = "item-stats").replace('<br>', '\n').get_text(separator=" ").strip()

                # print(item_card)


@bot.event
async def on_ready():
    guild = dc.Object(id=tk.GUILD)
    print("guild:", guild)
    print(f"Bot is ready to be used. Logged as {bot.user}")

# %%
### --------------------------- Main Code Below ---------------------------- ### 

if __name__ == "__main__":
    import requests as rq
    resp = rq.get("https://www.poewiki.net/wiki/Headhunter")
    soup = bs(resp.text, 'html.parser')
    item_card = soup.find("span", class_ = lambda c: c and c.startswith("item-box"))
    bot.run(tk.BOT_TOKEN)