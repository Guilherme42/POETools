# %%
import TOKENS as tk
import scarab_regex_lib as srl

import re 
import time, datetime
import discord as dc
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup as bs
import difflib
from typing import Union, Dict, List

intents = dc.Intents.default()
intents.message_content = True

DE_COLOR = lambda x: re.sub(r'\033\[(\d+;?)+m', x)


class myBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(Funcs(self))

bot = myBot(command_prefix="!", intents=intents, description="discord utilities for poe1. You can embed wiki queries into messages with [[item]]")

wikilink    = f"http://www.poewiki.net/wiki/"
wikipure    = f"http://www.poewiki.net/"
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
    
    await check_message_for_embedded_wiki_query(ctx)
    # on_message is an existing event that is being overwritten. This is needed to ensure the other ! commands still work.
    await bot.process_commands(ctx)

async def check_message_for_embedded_wiki_query(ctx: dc.message.Message):
    # Check if the message contains the [[ ]] tag to search.
    pattern = r"\[\[(.*?)\]\]"
    matches = re.search(pattern, ctx.content)
    closest_match = ""
    if matches:
        # print(f"match: {matches}")
        # print(f"possible search for {matches.group(1)}: {wikilink}{matches.group(1).replace(' ','_')}")
        # await ctx.channel.send(f"{wikilink}{matches.group(1).replace(' ','_')}")
        ret = await search_wiki_titles(matches.group(1), limit = 20)
        closest_match = ret[0] if ret else ""
    if closest_match:    
        wikiexists = f'{wikilink}{closest_match.replace(' ','_')}'
        embed = await create_embed_from_wiki(closest_match, wikiexists)
        if embed:
            await ctx.channel.send(embed=embed)

async def create_embed_from_wiki(title: str, url: str) -> dc.Embed:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.text()
                soup = bs(data, 'html.parser')
                allp = soup.find('div', class_='mw-parser-output').find_all('p')
                text_snippet = '\n'.join([p.get_text() for p in allp])
                if len(text_snippet) > 700:
                    text_snippet = text_snippet[:700] + '...' # grabs 700 initial characters
                # checks if there is an item card
                embed = dc.Embed(
                    color=dc.Color.blurple(),
                    title=f"Wiki: {title}",
                    description=text_snippet,
                    url=url
                )
                item_card = soup.find('div', class_="infobox-page-container").find("span", class_ = lambda c: c and c.startswith("item-box"))
                if item_card:
                    imglink = item_card.find('img').get('src')
                    print(f"{wikipure}{imglink}")
                    embed.set_image(url=f"{wikipure}{imglink}")
            else:
                return None
    return embed

def list_price(price_list: Dict[str, float], names: List[str]) -> str:
    returnstr = "```python\n"
    prices = price_list.items()
    names = [n[1:-1] for n in names] # Removes regex anchors from names
    largest_name = len(max(names, key=len))
    for p in prices:
        if p[0][1:-1] in names:
            returnstr += f"{p[0][1:-1]: <{largest_name}} = {p[1]:.2f}c\n"
    return returnstr + "```"

@bot.tree.command(name="scarab_regex", description="Generates regex to vendor scarabs.")
async def scarab_regex(interaction: dc.Interaction, treshold: float = 0.0):
    sr.update_value_treshold(treshold) if treshold else None
    text = sr.gen_scarab_regex(print_now=False)
    embed = dc.Embed(title="Regex generated",
                      description=f"```{text}```",
                      colour=0xf5ed00,
                      timestamp=sr.get_last_updated())
    embed.add_field(name="Price Threshold",
                    value=f"{sr.get_treshold()}c\nLast updated:",
                    inline=False)
    embed.set_thumbnail(url="https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvU2NhcmFicy9TdXBlclNjYXJhYjMiLCJzY2FsZSI6MX1d/64d9f06e78/SuperScarab3.png")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="scarab_prices", description="Lists the latest scarab prices.")
async def scarab_prices(interaction: dc.Interaction, treshold: float = 0.0):
    sr.update_value_treshold(treshold) if treshold else None
    sr.update_lists()

    embedb = dc.Embed(
        title="Below treshold:",
        description=f"{list_price(sr.prices, sr.sell)}",
        colour=0x24c1ff
        )
    embedb.set_thumbnail(url="https://web.poecdn.com/gen/image/WzI1LDE0LHsiZiI6IjJESXRlbXMvQ3VycmVuY3kvU2NhcmFicy9TdXBlclNjYXJhYjciLCJzY2FsZSI6MX1d/28b95bae7b/SuperScarab7.png")
    embeda = dc.Embed(
        title="Above treshold:",
        description=f"{list_price(sr.prices, sr.keep)}\nLast updated:",
        colour=0x24c1ff,
        timestamp=sr.get_last_updated()
        )
    await interaction.response.send_message(embed=embedb)
    await interaction.followup.send(embed=embeda)
    
@bot.tree.command(name="reload_commands", description="Reloads all bot commands." )
async def reload_commands(interaction: dc.Interaction):
    if interaction.user.id != tk.ME:
        await interaction.response.send_message("You are not authorized to use this command.")
    else:
        await bot.tree.sync()
        await interaction.response.send_message("Commands reloaded. press Ctrl+R to refresh the command list.")

@bot.tree.command(name="wiki", description="Searches poewiki for the item. You can also embed queries with [[item]]")
async def wiki(interaction: dc.Interaction, item: str):
    # tells discord to wait a bit
    await interaction.response.defer()
    # Assemble url to fetch from the wiki.
    url = f"{wikilink}{item.replace(' ','_')}"
    embed = await create_embed_from_wiki(item, url)
    # await scrape_wiki_for_item_card(url)
    # sends the response once ready
    await interaction.followup.send(embed=embed)

@wiki.autocomplete("item")
async def wiki_autocomplete(interaction: dc.Interaction, current: str):
    current = current.strip()
    if not current:
        return []
    # Use the shared search helper to get ranked (title, score) pairs
    ranked = await search_wiki_titles(current, limit=15)
    # return only top 5 as Choices
    return [dc.app_commands.Choice(name=title, value=title) for title in ranked[:5]]

# Searches the wiki for titles, given a query
async def search_wiki_titles(query: str, limit: int = 15) -> List[str]:
    """Search the POE wiki for titles matching any of the words in `query`.

    Returns a list of (title, score) tuples ordered by descending score.
    The scoring considers both string similarity and how many query words appear in the title.
    """
    query = (query or "").strip()
    if not query:
        return []

    words = [w for w in re.split(r"\s+", query.lower()) if w]
    # Build a search that matches any of the words in the title (prefix match)
    if words:
        srsearch = " OR ".join([f"intitle:{w}*" for w in words])
    else:
        srsearch = query

    titles = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            searchlink,
            params={
                "action": "query",
                "list": "search",
                "srsearch": srsearch,
                "srlimit": limit,
                "format": "json"
            }
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                results = data.get("query", {}).get("search", [])
                more = [s.get('title') for s in results if s.get('title') and not re.search(r"may refer to", s.get('snippet', ''))]
                titles.extend(more)

    # deduplicate while preserving order
    seen = set()
    uniq = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            uniq.append(t)

    # rank: combine sequence matcher ratio and word overlap
    ranked = []
    qlow = query.lower()
    for t in uniq:
        tlow = t.lower()
        ratio = difflib.SequenceMatcher(a=qlow, b=tlow).ratio()
        words_in = sum(1 for w in words if w in tlow)
        overlap = words_in / max(len(words), 1)
        score = ratio * 0.6 + overlap * 0.4
        ranked.append((t, score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    # returns only the titles in rankingorder
    return [r[0] for r in ranked] 

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
    # import requests as rq
    # resp = rq.get("https://www.poewiki.net/wiki/Headhunter")
    # soup = bs(resp.text, 'html.parser')
    # item_card = soup.find("span", class_ = lambda c: c and c.startswith("item-box"))
    sr = srl.scarab_regexer()
    bot.run(tk.BOT_TOKEN)