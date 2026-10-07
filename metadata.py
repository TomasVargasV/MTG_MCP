"""
Metadata definitions for the Scryfall MCP server.

Contains the lists of included/excluded fields and tools,
with descriptions for each. Used by the get_server_info tool
so the LLM knows what it can and cannot access.
"""

# ---------------------------------------------------------------------------
# Included card fields — these are returned by the server
# ---------------------------------------------------------------------------
INCLUDED_FIELDS = {
    # Identity & Metadata
    "id": "UUID — Unique Scryfall ID for this card object.",
    "oracle_id": "UUID — Shared identity across all printings of the same card.",
    "tcgplayer_id": "Integer — TCGplayer product ID.",
    "name": "String — Card name. Multi-face cards join names with ' // '.",
    "layout": "String — Card layout (normal, split, flip, transform, modal_dfc, adventure, meld, etc.).",
    "released_at": "Date — Release date of this printing.",
    "uri": "URI — API link to this card on Scryfall.",
    "rulings_uri": "URI — API link to this card's rulings.",

    # Gameplay
    "mana_cost": "String — Mana cost in Scryfall notation (e.g. {2}{U}{U}). Empty for lands.",
    "cmc": "Decimal — Mana value (converted mana cost).",
    "type_line": "String — Full type line (e.g. 'Legendary Creature — Human Wizard').",
    "oracle_text": "String — Official Oracle rules text.",
    "power": "String — Power (creatures only). Can be '*' or other non-numeric values.",
    "toughness": "String — Toughness (creatures only). Can be '*' or other non-numeric values.",
    "loyalty": "String — Starting loyalty (planeswalkers only).",
    "defense": "String — Defense value (battles only).",
    "life_modifier": "String — Life modifier (Vanguard cards only).",
    "hand_modifier": "String — Hand size modifier (Vanguard cards only).",
    "colors": "String[] — Colors of this card (W, U, B, R, G).",
    "color_identity": "String[] — Color identity for Commander format.",
    "color_indicator": "String[] — Color indicator for cards without mana costs.",
    "keywords": "String[] — Keyword abilities on this card (Flying, Trample, etc.).",
    "produced_mana": "String[] — Colors of mana this card can produce.",
    "all_parts": "Object[] — Related card parts (tokens created, meld pairs, etc.).",
    "card_faces": "Object[] — Face objects for multi-face cards. Each face has its own name, mana_cost, oracle_text, type_line, power, toughness, etc.",
    "legalities": "Object — Map of format name to legality status (legal, not_legal, restricted, banned).",
    "games": "String[] — Games this printing appears in (paper, mtgo, arena).",
    "reserved": "Boolean — Whether this card is on the Reserved List.",

    # Print details
    "set": "String — Set code (e.g. 'mh2', 'dmu').",
    "set_name": "String — Full set name.",
    "set_type": "String — Set type (expansion, core, masters, draft_innovation, etc.).",
    "rarity": "String — Rarity: common, uncommon, rare, mythic, special, bonus.",
    "digital": "Boolean — Whether this is a digital-only printing.",
    "flavor_name": "String — Alternate card name (e.g. Godzilla series).",
    "reprint": "Boolean — Whether this printing is a reprint.",
    "variation": "Boolean — Whether this printing is a variation of another.",
    "variation_of": "UUID — Scryfall ID of the card this is a variation of.",

    # Prices
    "prices.usd": "String — Current USD price (nonfoil).",
}

# The set of field keys to keep when filtering card objects
INCLUDED_FIELD_KEYS = {
    "id", "oracle_id", "tcgplayer_id", "name", "layout", "released_at",
    "uri", "rulings_uri",
    "mana_cost", "cmc", "type_line", "oracle_text", "power", "toughness",
    "loyalty", "defense", "life_modifier", "hand_modifier",
    "colors", "color_identity", "color_indicator", "keywords",
    "produced_mana", "all_parts", "card_faces", "legalities", "games",
    "reserved",
    "set", "set_name", "set_type", "rarity", "digital", "flavor_name",
    "reprint", "variation", "variation_of",
    "prices",  # We'll filter prices sub-fields separately
}

# ---------------------------------------------------------------------------
# Excluded card fields — NOT returned, but documented so the LLM can explain
# ---------------------------------------------------------------------------
EXCLUDED_FIELDS = {
    "multiverse_ids": {
        "type": "Integer[]",
        "description": "Gatherer Multiverse IDs for this card.",
        "reason": "Cross-referencing with Gatherer.",
    },
    "mtgo_id": {
        "type": "Integer",
        "description": "This card's MTGO catalog ID.",
        "reason": "MTGO-specific lookups.",
    },
    "mtgo_foil_id": {
        "type": "Integer",
        "description": "This card's MTGO foil catalog ID.",
        "reason": "MTGO foil pricing and lookups.",
    },
    "arena_id": {
        "type": "Integer",
        "description": "This card's MTG Arena ID.",
        "reason": "Arena-specific lookups.",
    },
    "cardmarket_id": {
        "type": "Integer",
        "description": "This card's Cardmarket ID.",
        "reason": "Cardmarket cross-reference.",
    },
    "lang": {
        "type": "String",
        "description": "Language code for this printing.",
        "reason": "Multi-language card support.",
    },
    "scryfall_uri": {
        "type": "URI",
        "description": "Link to this card's page on the Scryfall website.",
        "reason": "Providing browseable links to users.",
    },
    "prints_search_uri": {
        "type": "URI",
        "description": "API link to search for all printings of this card.",
        "reason": "Finding all printings of a card.",
    },
    "collector_number": {
        "type": "String",
        "description": "Collector number within the set.",
        "reason": "Identifying exact printings by collector number.",
    },
    "artist": {
        "type": "String",
        "description": "The artist who illustrated this card.",
        "reason": "Art and artist queries.",
    },
    "artist_ids": {
        "type": "UUID[]",
        "description": "Scryfall IDs for the artist(s).",
        "reason": "Artist lookups by ID.",
    },
    "illustration_id": {
        "type": "UUID",
        "description": "Shared ID across printings with the same artwork.",
        "reason": "Tracking art variants across printings.",
    },
    "border_color": {
        "type": "String",
        "description": "Card border color: black, white, borderless, silver, gold.",
        "reason": "Printing aesthetics and variant identification.",
    },
    "frame": {
        "type": "String",
        "description": "Frame year style (1993, 1997, 2003, 2015, future).",
        "reason": "Frame style queries and vintage identification.",
    },
    "frame_effects": {
        "type": "String[]",
        "description": "Special frame effects (legendary, miracle, nyxtouched, colorshifted, etc.).",
        "reason": "Visual variant and special frame queries.",
    },
    "security_stamp": {
        "type": "String",
        "description": "Security stamp type: oval, triangle, acorn, arena, heart.",
        "reason": "Identifying card legality category (acorn = not tournament legal).",
    },
    "full_art": {
        "type": "Boolean",
        "description": "Whether this printing is full art.",
        "reason": "Art variant queries.",
    },
    "textless": {
        "type": "Boolean",
        "description": "Whether this printing has no rules text printed.",
        "reason": "Promo and variant identification.",
    },
    "booster": {
        "type": "Boolean",
        "description": "Whether this card can be found in booster packs.",
        "reason": "Product and availability queries.",
    },
    "story_spotlight": {
        "type": "Boolean",
        "description": "Whether this is a Story Spotlight card.",
        "reason": "Lore and story queries.",
    },
    "promo": {
        "type": "Boolean",
        "description": "Whether this printing is a promo.",
        "reason": "Promo identification.",
    },
    "promo_types": {
        "type": "String[]",
        "description": "Types of promo (datestamped, buyabox, prerelease, etc.).",
        "reason": "Promo classification.",
    },
    "flavor_text": {
        "type": "String",
        "description": "The flavor text on this printing.",
        "reason": "Lore and flavor text queries.",
    },
    "finishes": {
        "type": "String[]",
        "description": "Available finishes: foil, nonfoil, etched.",
        "reason": "Foil and finish availability queries.",
    },
    "watermark": {
        "type": "String",
        "description": "Watermark name on this printing.",
        "reason": "Watermark queries.",
    },
    "oversized": {
        "type": "Boolean",
        "description": "Whether this is an oversized card.",
        "reason": "Product identification (planechase, archenemy, etc.).",
    },
    "content_warning": {
        "type": "Boolean",
        "description": "Whether this card has a content warning.",
        "reason": "Content filtering.",
    },
    "highres_image": {
        "type": "Boolean",
        "description": "Whether a high-resolution scan is available.",
        "reason": "Image quality checks.",
    },
    "image_status": {
        "type": "String",
        "description": "Image availability status: missing, placeholder, lowres, highres_scan.",
        "reason": "Image availability checks.",
    },
    "image_uris": {
        "type": "Object",
        "description": "URLs for card images in multiple sizes (small, normal, large, png, art_crop, border_crop).",
        "reason": "Displaying card images.",
    },
    "prices.usd_foil": {
        "type": "String",
        "description": "Current USD price for foil version.",
        "reason": "Foil pricing.",
    },
    "prices.usd_etched": {
        "type": "String",
        "description": "Current USD price for etched foil version.",
        "reason": "Etched foil pricing.",
    },
    "prices.eur": {
        "type": "String",
        "description": "Current EUR price (nonfoil).",
        "reason": "European market pricing.",
    },
    "prices.eur_foil": {
        "type": "String",
        "description": "Current EUR price for foil version.",
        "reason": "European foil pricing.",
    },
    "prices.tix": {
        "type": "String",
        "description": "Current MTGO tix price.",
        "reason": "MTGO economy pricing.",
    },
    "purchase_uris": {
        "type": "Object",
        "description": "Links to buy on TCGplayer, Cardmarket, and Cardhoarder.",
        "reason": "Direct purchase links.",
    },
    "related_uris": {
        "type": "Object",
        "description": "Links to Gatherer, EDHRec, TCGplayer Decks, etc.",
        "reason": "External resource cross-references.",
    },
}

# ---------------------------------------------------------------------------
# Excluded tools — API endpoints NOT exposed by this server
# ---------------------------------------------------------------------------
EXCLUDED_TOOLS = {
    "get_random_card": {
        "endpoint": "GET /cards/random",
        "description": "Returns a random card, optionally filtered by a search query.",
        "reason": "Discovery and brewing inspiration.",
    },
    "get_card_by_set_and_lang": {
        "endpoint": "GET /cards/:code/:number/:lang",
        "description": "Fetches a card by set code, collector number, and language.",
        "reason": "Non-English card lookups.",
    },
    "get_card_by_multiverse": {
        "endpoint": "GET /cards/multiverse/:id",
        "description": "Fetches a card by its Gatherer Multiverse ID.",
        "reason": "Gatherer cross-reference.",
    },
    "get_card_by_mtgo": {
        "endpoint": "GET /cards/mtgo/:id",
        "description": "Fetches a card by its MTGO ID.",
        "reason": "MTGO-specific lookups.",
    },
    "get_card_by_arena": {
        "endpoint": "GET /cards/arena/:id",
        "description": "Fetches a card by its MTG Arena ID.",
        "reason": "Arena-specific lookups.",
    },
    "get_card_by_tcgplayer": {
        "endpoint": "GET /cards/tcgplayer/:id",
        "description": "Fetches a card by its TCGplayer ID.",
        "reason": "TCGplayer cross-reference.",
    },
    "get_rulings_by_multiverse": {
        "endpoint": "GET /cards/multiverse/:id/rulings",
        "description": "Returns rulings for a card using its Gatherer Multiverse ID.",
        "reason": "Rulings via Gatherer ID.",
    },
    "get_rulings_by_mtgo": {
        "endpoint": "GET /cards/mtgo/:id/rulings",
        "description": "Returns rulings for a card using its MTGO ID.",
        "reason": "Rulings via MTGO ID.",
    },
    "get_rulings_by_arena": {
        "endpoint": "GET /cards/arena/:id/rulings",
        "description": "Returns rulings for a card using its Arena ID.",
        "reason": "Rulings via Arena ID.",
    },
    "get_set_by_id": {
        "endpoint": "GET /sets/:id",
        "description": "Fetches a set by its Scryfall UUID.",
        "reason": "Set lookup by internal ID.",
    },
    "get_set_by_tcgplayer": {
        "endpoint": "GET /sets/tcgplayer/:id",
        "description": "Fetches a set by its TCGplayer group ID.",
        "reason": "TCGplayer set cross-reference.",
    },
    "catalog_artist_names": {
        "endpoint": "GET /catalog/artist-names",
        "description": "Returns all artist names in Scryfall's database.",
        "reason": "Artist queries.",
    },
    "catalog_watermarks": {
        "endpoint": "GET /catalog/watermarks",
        "description": "Returns all watermark names.",
        "reason": "Watermark queries.",
    },
}

# ---------------------------------------------------------------------------
# Included tools — summary for the info endpoint
# ---------------------------------------------------------------------------
INCLUDED_TOOLS = {
    "search_cards": {
        "endpoint": "GET /cards/search",
        "description": "Full-text search using Scryfall query syntax (colors, types, mana value, sets, formats, oracle text, and more).",
    },
    "get_card_by_name": {
        "endpoint": "GET /cards/named",
        "description": "Find a card by exact or fuzzy name match.",
    },
    "autocomplete_card_name": {
        "endpoint": "GET /cards/autocomplete",
        "description": "Get up to 20 card name completions from a partial string.",
    },
    "get_card_collection": {
        "endpoint": "POST /cards/collection",
        "description": "Fetch up to 75 cards at once by identifiers (name, id, set+number, etc.).",
    },
    "get_card_by_id": {
        "endpoint": "GET /cards/:id",
        "description": "Fetch a single card by its Scryfall UUID.",
    },
    "get_card_by_set": {
        "endpoint": "GET /cards/:code/:number",
        "description": "Fetch a card by set code and collector number.",
    },
    "get_card_by_cardmarket": {
        "endpoint": "GET /cards/cardmarket/:id",
        "description": "Fetch a card by its Cardmarket ID.",
    },
    "get_rulings_by_id": {
        "endpoint": "GET /cards/:id/rulings",
        "description": "Get official Oracle rulings for a card by Scryfall ID.",
    },
    "get_rulings_by_set": {
        "endpoint": "GET /cards/:code/:number/rulings",
        "description": "Get official Oracle rulings for a card by set code and collector number.",
    },
    "list_sets": {
        "endpoint": "GET /sets",
        "description": "List all MTG sets with codes, names, release dates, and card counts.",
    },
    "get_set": {
        "endpoint": "GET /sets/:code",
        "description": "Get a specific set by its code.",
    },
    "list_symbols": {
        "endpoint": "GET /symbology",
        "description": "List all mana and rules-text symbols with their meanings.",
    },
    "parse_mana_cost": {
        "endpoint": "GET /symbology/parse-mana",
        "description": "Parse a mana cost string into structured data (colors, CMC, etc.).",
    },
    "catalog_card_names": {
        "endpoint": "GET /catalog/card-names",
        "description": "Get all nontoken English card names.",
    },
    "catalog_word_bank": {
        "endpoint": "GET /catalog/word-bank",
        "description": "Get all unique words used in card names and oracle text.",
    },
    "catalog_creature_types": {
        "endpoint": "GET /catalog/creature-types",
        "description": "Get all creature types (Human, Elf, Dragon, etc.).",
    },
    "catalog_planeswalker_types": {
        "endpoint": "GET /catalog/planeswalker-types",
        "description": "Get all planeswalker types (Jace, Chandra, etc.).",
    },
    "catalog_land_types": {
        "endpoint": "GET /catalog/land-types",
        "description": "Get all land types (Forest, Island, Urza's, etc.).",
    },
    "catalog_artifact_types": {
        "endpoint": "GET /catalog/artifact-types",
        "description": "Get all artifact types (Equipment, Vehicle, etc.).",
    },
    "catalog_enchantment_types": {
        "endpoint": "GET /catalog/enchantment-types",
        "description": "Get all enchantment types (Aura, Saga, etc.).",
    },
    "catalog_spell_types": {
        "endpoint": "GET /catalog/spell-types",
        "description": "Get all spell types (Arcane, Trap, etc.).",
    },
    "catalog_powers": {
        "endpoint": "GET /catalog/powers",
        "description": "Get all possible power values.",
    },
    "catalog_toughnesses": {
        "endpoint": "GET /catalog/toughnesses",
        "description": "Get all possible toughness values.",
    },
    "catalog_loyalties": {
        "endpoint": "GET /catalog/loyalties",
        "description": "Get all possible starting loyalty values.",
    },
    "catalog_keyword_abilities": {
        "endpoint": "GET /catalog/keyword-abilities",
        "description": "Get all keyword abilities (Flying, Trample, Deathtouch, etc.).",
    },
    "catalog_keyword_actions": {
        "endpoint": "GET /catalog/keyword-actions",
        "description": "Get all keyword actions (Destroy, Exile, Scry, etc.).",
    },
    "catalog_ability_words": {
        "endpoint": "GET /catalog/ability-words",
        "description": "Get all ability words (Landfall, Revolt, Constellation, etc.).",
    },
    "catalog_supertypes": {
        "endpoint": "GET /catalog/supertypes",
        "description": "Get all supertypes (Legendary, Basic, Snow, World, etc.).",
    },
    "list_bulk_data": {
        "endpoint": "GET /bulk-data",
        "description": "List available bulk data download files (full database dumps).",
    },
    "list_migrations": {
        "endpoint": "GET /migrations",
        "description": "List card-object migration records (merges, splits).",
    },
    "get_server_info": {
        "endpoint": "N/A (local)",
        "description": "Returns metadata about this MCP server: included/excluded fields, included/excluded tools, and their descriptions.",
    },
}
