"""
Scryfall MCP Server

An MCP server that provides access to the Scryfall Magic: The Gathering
card database. Exposes 31 tools for searching cards, fetching rulings,
browsing sets, symbology, catalogs, bulk data, and migrations.

All card responses are filtered to a curated set of fields.
A get_server_info tool exposes metadata about included/excluded
fields and tools so the LLM can explain its own limitations.
"""

import json
import sys
import os

# Add the server directory to the path so metadata imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

from scryfall_client import ScryfallClient
from metadata import (
    INCLUDED_FIELDS,
    EXCLUDED_FIELDS,
    INCLUDED_TOOLS,
    EXCLUDED_TOOLS,
)

# Initialize MCP server and Scryfall client
mcp = FastMCP(
    "scryfall-mtg",
    instructions="""You are connected to the Scryfall MCP server, which provides
access to the complete Magic: The Gathering card database via the Scryfall API.

CRITICAL RULES — CARD DATA:
1. NEVER recall card data from memory. ALWAYS use the tools to look up cards.
2. When a user mentions a card, call get_card_by_name BEFORE responding.
3. When discussing card interactions, look up ALL cards involved.
4. If a search returns no results, try fuzzy name matching or autocomplete.
5. Always quote oracle_text exactly as returned — never paraphrase rules text.
6. If the user asks for information that requires an excluded field or tool,
   call get_server_info and explain what is unavailable and why.

WORKFLOW — GROUND, REASON, SEARCH, VERIFY:
When the user asks about combos, synergies, meta viability, deck building strategy,
or any strategic/community-sourced knowledge, follow this four-step workflow:

Step 1 — GROUND: Look up ALL relevant cards via the Scryfall tools first.
  Get the real oracle text, rulings, legalities, and keywords into context
  before doing anything else.

Step 2 — REASON: Before searching the web, analyze the cards yourself using ONLY
  the Scryfall data you just retrieved. Form your own independent assessment:
  - What combos or synergies do you see based on the oracle text?
  - What interactions stand out from the rules text and keywords?
  - What strengths, weaknesses, or caveats do you notice?
  - What other cards might synergize based on mechanics and type lines?
  Present this analysis to the user as YOUR OWN reasoning. This must happen
  BEFORE any web search so your thinking is not biased by external opinions.
  Label this section clearly (e.g. "Based on the card text, here's what I see:").

Step 3 — SEARCH: Now search the web for community knowledge — combos, synergies,
  meta discussion, rulings edge cases, deck techs, and creative interactions.
  Prioritize results from these MTG community sources:
  - EDHRec (edhrec.com) — Commander combos, synergies, staples
  - MTGGoldfish (mtggoldfish.com) — meta decks, price trends, format staples
  - Moxfield (moxfield.com) — decklists and community brews
  - MTG Salvation, Reddit r/magicTCG, r/EDH, r/CompetitiveEDH, r/ModernMagic
  - ChannelFireball, Star City Games — strategy articles

Step 4 — VERIFY & SYNTHESIZE: Cross-reference and combine both perspectives:
  a) Verify every card-related claim from web results against Scryfall data:
     - If a web source says a card does something, check the oracle_text.
     - If a web source claims a combo works, verify the interaction using the
       actual rules text of all cards involved.
     - If a web source says a card is legal/banned in a format, check legalities.
     - If a web source gets a card wrong, flag it to the user:
       "Note: [source] describes [card] incorrectly. The actual oracle text is: ..."
  b) Compare your Step 2 analysis with what the community found:
     - Highlight combos or ideas you identified that the community also uses.
     - Highlight combos the community found that you missed — look these up on
       Scryfall and verify they work.
     - Highlight any original ideas from your own analysis that the community
       hasn't widely discussed — these may be hidden gems or may have flaws
       the community already discovered.
  Label community-sourced findings clearly so the user knows what came from
  your reasoning vs. what came from external sources.

This workflow ensures the user gets unbiased independent analysis, verified community
knowledge, and a clear comparison of both — without web sources contaminating
the LLM's own reasoning or introducing incorrect card information.

The server filters card responses to a curated set of gameplay-relevant fields.
Use get_server_info to see the full list of included and excluded fields/tools.""",
)

client = ScryfallClient()


def _to_json(data: dict) -> str:
    """Convert a dict to a formatted JSON string for the LLM."""
    return json.dumps(data, indent=2, ensure_ascii=False)


# ======================================================================
# CARD TOOLS
# ======================================================================


@mcp.tool()
async def search_cards(
    query: str,
    unique: str = "cards",
    order: str = "name",
    direction: str = "auto",
    page: int = 1,
) -> str:
    """Search for Magic: The Gathering cards using Scryfall query syntax.

    The query supports the full Scryfall search syntax:
    - Colors: c:red, c:ub, c>=rg
    - Types: t:creature, t:instant, t:legendary
    - Mana value: mv=3, mv>=5, cmc<2
    - Oracle text: o:flying, o:"draw a card"
    - Power/toughness: pow>=4, tou=1
    - Sets: s:mh2, s:dmu
    - Format legality: f:modern, f:standard, f:commander
    - Rarity: r:mythic, r:rare
    - Keywords: keyword:flying, keyword:trample
    - Combinations: c:red t:creature mv<=3 f:modern

    Args:
        query: Scryfall search query string.
        unique: How to handle duplicates: "cards" (default), "art", or "prints".
        order: Sort order: "name", "released", "set", "rarity", "color",
               "usd", "cmc", "power", "toughness", "edhrec", "penny", "artist", "review".
        direction: Sort direction: "auto" (default), "asc", or "desc".
        page: Page number for paginated results (default 1).

    Returns:
        JSON with matching cards (filtered to included fields) and pagination info.
    """
    result = await client.search_cards(query, unique, order, direction, page)
    return _to_json(result)


@mcp.tool()
async def get_card_by_name(
    name: str,
    fuzzy: bool = True,
    set_code: str = None,
) -> str:
    """Find a specific Magic: The Gathering card by name.

    Use this tool whenever you need to look up a specific card. Supports
    fuzzy matching to handle typos and partial names.

    IMPORTANT: Always call this tool before discussing any specific card.
    Never rely on memory for card data.

    Args:
        name: The card name to search for.
        fuzzy: If True (default), uses fuzzy matching to handle typos.
               If False, requires an exact name match.
        set_code: Optional set code to get a specific printing (e.g. "mh2").

    Returns:
        JSON with the card data (filtered to included fields).
    """
    result = await client.get_card_by_name(name, fuzzy, set_code)
    return _to_json(result)


@mcp.tool()
async def autocomplete_card_name(query: str) -> str:
    """Get card name autocompletions from a partial string.

    Returns up to 20 card names that match the partial input.
    Useful when you are unsure of the exact card name or the user
    gave an incomplete name.

    Args:
        query: Partial card name string.

    Returns:
        JSON with a list of up to 20 matching card names.
    """
    result = await client.autocomplete_card_name(query)
    return _to_json(result)


@mcp.tool()
async def get_card_collection(identifiers: list) -> str:
    """Fetch multiple cards at once by their identifiers.

    Accepts up to 75 card identifiers in a single request.
    Useful for looking up entire decklists.

    Each identifier is a dict with one of these schemas:
    - {"name": "Lightning Bolt"}
    - {"id": "<scryfall-uuid>"}
    - {"set": "mh2", "collector_number": "130"}
    - {"name": "Lightning Bolt", "set": "2xm"}

    Args:
        identifiers: List of identifier dicts (max 75).

    Returns:
        JSON with the matched cards (filtered to included fields).
    """
    result = await client.get_card_collection(identifiers)
    return _to_json(result)


@mcp.tool()
async def get_card_by_id(scryfall_id: str) -> str:
    """Fetch a card by its Scryfall UUID.

    Use this when you already have a card's Scryfall ID from a
    previous search or lookup.

    Args:
        scryfall_id: The Scryfall UUID of the card.

    Returns:
        JSON with the card data (filtered to included fields).
    """
    result = await client.get_card_by_id(scryfall_id)
    return _to_json(result)


@mcp.tool()
async def get_card_by_set(set_code: str, collector_number: str) -> str:
    """Fetch a card by its set code and collector number.

    Identifies a specific printing of a card.

    Args:
        set_code: The set code (e.g. "mh2", "dmu", "lci").
        collector_number: The collector number within the set.

    Returns:
        JSON with the card data (filtered to included fields).
    """
    result = await client.get_card_by_set(set_code, collector_number)
    return _to_json(result)


@mcp.tool()
async def get_card_by_cardmarket(cardmarket_id: int) -> str:
    """Fetch a card by its Cardmarket ID.

    Args:
        cardmarket_id: The Cardmarket product ID.

    Returns:
        JSON with the card data (filtered to included fields).
    """
    result = await client.get_card_by_cardmarket(cardmarket_id)
    return _to_json(result)


# ======================================================================
# RULINGS TOOLS
# ======================================================================


@mcp.tool()
async def get_rulings_by_id(scryfall_id: str) -> str:
    """Get official Oracle rulings for a card by its Scryfall ID.

    Returns rulings from Wizards of the Coast, set release notes,
    and Scryfall-authored notes.

    Args:
        scryfall_id: The Scryfall UUID of the card.

    Returns:
        JSON with a list of ruling objects (source, published_at, comment).
    """
    result = await client.get_rulings_by_id(scryfall_id)
    return _to_json(result)


@mcp.tool()
async def get_rulings_by_set(set_code: str, collector_number: str) -> str:
    """Get official Oracle rulings for a card by set code and collector number.

    Args:
        set_code: The set code (e.g. "mh2").
        collector_number: The collector number within the set.

    Returns:
        JSON with a list of ruling objects (source, published_at, comment).
    """
    result = await client.get_rulings_by_set(set_code, collector_number)
    return _to_json(result)


# ======================================================================
# SET TOOLS
# ======================================================================


@mcp.tool()
async def list_sets() -> str:
    """List all Magic: The Gathering sets.

    Returns all sets with their codes, names, release dates,
    card counts, and set types.

    Returns:
        JSON with a list of all set objects.
    """
    result = await client.list_sets()
    return _to_json(result)


@mcp.tool()
async def get_set(set_code: str) -> str:
    """Get details about a specific Magic: The Gathering set.

    Args:
        set_code: The set code (e.g. "mh2", "dmu", "lci", "mkm").

    Returns:
        JSON with the set object (name, code, release date, card count, etc.).
    """
    result = await client.get_set(set_code)
    return _to_json(result)


# ======================================================================
# SYMBOLOGY TOOLS
# ======================================================================


@mcp.tool()
async def list_symbols() -> str:
    """List all card symbols used in Magic: The Gathering.

    Returns all mana symbols, tap symbols, loyalty symbols, etc.
    with their text representations and meanings.

    Returns:
        JSON with a list of symbol objects.
    """
    result = await client.list_symbols()
    return _to_json(result)


@mcp.tool()
async def parse_mana_cost(cost: str) -> str:
    """Parse a mana cost string into structured data.

    Takes a mana cost like "3UU" or "{2}{W}{W}" and returns
    the normalized representation, colors, and converted mana cost.

    Args:
        cost: The mana cost string to parse.

    Returns:
        JSON with the parsed mana cost (normalized cost, cmc, colors).
    """
    result = await client.parse_mana_cost(cost)
    return _to_json(result)


# ======================================================================
# CATALOG TOOLS
# ======================================================================


@mcp.tool()
async def catalog_card_names() -> str:
    """Get all nontoken English card names in Scryfall's database.

    Returns:
        JSON with a catalog object containing all card names.
    """
    result = await client.get_catalog("card-names")
    return _to_json(result)


@mcp.tool()
async def catalog_word_bank() -> str:
    """Get all unique words used in Magic card names and oracle text.

    Returns:
        JSON with a catalog of all unique words.
    """
    result = await client.get_catalog("word-bank")
    return _to_json(result)


@mcp.tool()
async def catalog_creature_types() -> str:
    """Get all creature types in Magic: The Gathering.

    Examples: Human, Elf, Dragon, Goblin, Merfolk, Zombie, etc.

    Returns:
        JSON with a catalog of all creature types.
    """
    result = await client.get_catalog("creature-types")
    return _to_json(result)


@mcp.tool()
async def catalog_planeswalker_types() -> str:
    """Get all planeswalker types in Magic: The Gathering.

    Examples: Jace, Chandra, Liliana, Nissa, Ajani, etc.

    Returns:
        JSON with a catalog of all planeswalker types.
    """
    result = await client.get_catalog("planeswalker-types")
    return _to_json(result)


@mcp.tool()
async def catalog_land_types() -> str:
    """Get all land types in Magic: The Gathering.

    Includes basic types (Forest, Island, Mountain, Plains, Swamp)
    and nonbasic types (Urza's, Mine, Tower, etc.).

    Returns:
        JSON with a catalog of all land types.
    """
    result = await client.get_catalog("land-types")
    return _to_json(result)


@mcp.tool()
async def catalog_artifact_types() -> str:
    """Get all artifact types in Magic: The Gathering.

    Examples: Equipment, Vehicle, Food, Treasure, Clue, Blood, etc.

    Returns:
        JSON with a catalog of all artifact types.
    """
    result = await client.get_catalog("artifact-types")
    return _to_json(result)


@mcp.tool()
async def catalog_enchantment_types() -> str:
    """Get all enchantment types in Magic: The Gathering.

    Examples: Aura, Saga, Shrine, Cartouche, Curse, etc.

    Returns:
        JSON with a catalog of all enchantment types.
    """
    result = await client.get_catalog("enchantment-types")
    return _to_json(result)


@mcp.tool()
async def catalog_spell_types() -> str:
    """Get all spell types in Magic: The Gathering.

    Examples: Arcane, Trap, Adventure, Lesson, etc.

    Returns:
        JSON with a catalog of all spell types.
    """
    result = await client.get_catalog("spell-types")
    return _to_json(result)


@mcp.tool()
async def catalog_powers() -> str:
    """Get all possible power values for creatures.

    Includes numeric values and special values like *.

    Returns:
        JSON with a catalog of all power values.
    """
    result = await client.get_catalog("powers")
    return _to_json(result)


@mcp.tool()
async def catalog_toughnesses() -> str:
    """Get all possible toughness values for creatures.

    Includes numeric values and special values like *.

    Returns:
        JSON with a catalog of all toughness values.
    """
    result = await client.get_catalog("toughnesses")
    return _to_json(result)


@mcp.tool()
async def catalog_loyalties() -> str:
    """Get all possible starting loyalty values for planeswalkers.

    Returns:
        JSON with a catalog of all loyalty values.
    """
    result = await client.get_catalog("loyalties")
    return _to_json(result)


@mcp.tool()
async def catalog_keyword_abilities() -> str:
    """Get all keyword abilities in Magic: The Gathering.

    Examples: Flying, Trample, Deathtouch, Lifelink, Haste,
    First Strike, Double Strike, Vigilance, Hexproof, etc.

    Returns:
        JSON with a catalog of all keyword abilities.
    """
    result = await client.get_catalog("keyword-abilities")
    return _to_json(result)


@mcp.tool()
async def catalog_keyword_actions() -> str:
    """Get all keyword actions in Magic: The Gathering.

    Examples: Destroy, Exile, Sacrifice, Scry, Surveil,
    Mill, Fight, Adapt, Bolster, Explore, etc.

    Returns:
        JSON with a catalog of all keyword actions.
    """
    result = await client.get_catalog("keyword-actions")
    return _to_json(result)


@mcp.tool()
async def catalog_ability_words() -> str:
    """Get all ability words in Magic: The Gathering.

    Ability words are italicized words before an ability that
    group thematically related abilities. They have no rules meaning.

    Examples: Landfall, Revolt, Constellation, Delirium,
    Metalcraft, Threshold, Morbid, etc.

    Returns:
        JSON with a catalog of all ability words.
    """
    result = await client.get_catalog("ability-words")
    return _to_json(result)


@mcp.tool()
async def catalog_supertypes() -> str:
    """Get all supertypes in Magic: The Gathering.

    Examples: Legendary, Basic, Snow, World, Ongoing.

    Returns:
        JSON with a catalog of all supertypes.
    """
    result = await client.get_catalog("supertypes")
    return _to_json(result)


# ======================================================================
# BULK DATA & MIGRATIONS
# ======================================================================


@mcp.tool()
async def list_bulk_data() -> str:
    """List all available bulk data downloads from Scryfall.

    Bulk data files contain full database dumps (all cards, all rulings,
    etc.) as downloadable JSON files. Useful for building local databases.

    Returns:
        JSON with a list of bulk data items (type, name, download URI, updated_at).
    """
    result = await client.list_bulk_data()
    return _to_json(result)


@mcp.tool()
async def list_migrations() -> str:
    """List card-object migration records from Scryfall.

    Migrations track when Scryfall merges or splits card entries.
    Useful for keeping a local database in sync.

    Returns:
        JSON with a list of migration records.
    """
    result = await client.list_migrations()
    return _to_json(result)


# ======================================================================
# SERVER INFO (DISCOVERY / SELF-AWARENESS)
# ======================================================================


@mcp.tool()
async def get_server_info() -> str:
    """Get metadata about this MCP server's capabilities and limitations.

    Returns the complete list of:
    - Included fields: fields returned in card responses, with descriptions.
    - Excluded fields: fields NOT returned, with descriptions and reasons.
    - Included tools: available tools with their API endpoints.
    - Excluded tools: unavailable tools with their endpoints and reasons.

    Call this tool when:
    - The user asks for information you cannot find in card responses.
    - You need to explain why certain data is unavailable.
    - The user wants to know what the server can and cannot do.
    """
    info = {
        "server_name": "scryfall-mtg",
        "version": "1.0.0",
        "description": "MCP server for the Scryfall Magic: The Gathering card database.",
        "total_included_tools": len(INCLUDED_TOOLS),
        "total_excluded_tools": len(EXCLUDED_TOOLS),
        "total_included_fields": len(INCLUDED_FIELDS),
        "total_excluded_fields": len(EXCLUDED_FIELDS),
        "included_fields": INCLUDED_FIELDS,
        "excluded_fields": EXCLUDED_FIELDS,
        "included_tools": INCLUDED_TOOLS,
        "excluded_tools": EXCLUDED_TOOLS,
    }
    return _to_json(info)


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
