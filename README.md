# Scryfall MTG — MCP Server

An MCP (Model Context Protocol) server that connects AI assistants to the [Scryfall](https://scryfall.com/) Magic: The Gathering card database. Prevents AI hallucination by forcing the model to look up real card data before responding.

## What it does

- **31 tools** for searching cards, fetching rulings, browsing sets, symbology, catalogs, bulk data, and migrations
- **Field filtering** — card responses are stripped to gameplay-relevant fields, keeping the LLM's context window lean
- **Self-awareness** — a `get_server_info` tool tells the LLM what fields and tools are excluded, so it can explain its own limitations instead of guessing
- **Rate limiting** — respects Scryfall's API rate limits (100ms between requests)
- **Multi-face card support** — properly handles transform, MDFC, split, adventure, and flip cards

## Prerequisites

- Python 3.10 or higher
- pip

## Setup

### 1. Clone or copy the project

Place the `scryfall-mtg` folder wherever you like on your machine.

### 2. Create a virtual environment (recommended)

```bash
cd scryfall-mtg
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Test that it runs

```bash
python server.py
```

The server will start in stdio mode and wait for MCP messages. Press `Ctrl+C` to stop.

## Connecting to Claude Desktop

Edit your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "scryfall-mtg": {
      "command": "python",
      "args": ["C:/path/to/scryfall-mtg/server.py"],
      "env": {}
    }
  }
}
```

If using a virtual environment, point `command` to the venv's Python:

```json
{
  "mcpServers": {
    "scryfall-mtg": {
      "command": "C:/path/to/scryfall-mtg/.venv/Scripts/python.exe",
      "args": ["C:/path/to/scryfall-mtg/server.py"],
      "env": {}
    }
  }
}
```

Restart Claude Desktop after saving.

## Connecting to Joule Work Desktop

In Joule, go to **Settings > MCP Servers** and add a new connector:

- **Name:** Scryfall MTG
- **Command:** `python` (or the full path to your venv Python)
- **Args:** full path to `server.py`

## Available Tools (31)

### Card Search & Lookup (7)
| Tool | Description |
|---|---|
| `search_cards` | Full-text search using Scryfall query syntax |
| `get_card_by_name` | Find a card by exact or fuzzy name |
| `autocomplete_card_name` | Get up to 20 name completions from a partial string |
| `get_card_collection` | Fetch up to 75 cards at once (great for decklists) |
| `get_card_by_id` | Fetch a card by Scryfall UUID |
| `get_card_by_set` | Fetch a card by set code + collector number |
| `get_card_by_cardmarket` | Fetch a card by Cardmarket ID |

### Rulings (2)
| Tool | Description |
|---|---|
| `get_rulings_by_id` | Official rulings by Scryfall ID |
| `get_rulings_by_set` | Official rulings by set code + collector number |

### Sets (2)
| Tool | Description |
|---|---|
| `list_sets` | List all MTG sets |
| `get_set` | Get details about a specific set |

### Symbology (2)
| Tool | Description |
|---|---|
| `list_symbols` | List all mana/rules symbols |
| `parse_mana_cost` | Parse a mana cost string into structured data |

### Catalogs (15)
| Tool | Description |
|---|---|
| `catalog_card_names` | All nontoken English card names |
| `catalog_word_bank` | All unique words in card text |
| `catalog_creature_types` | All creature types |
| `catalog_planeswalker_types` | All planeswalker types |
| `catalog_land_types` | All land types |
| `catalog_artifact_types` | All artifact types |
| `catalog_enchantment_types` | All enchantment types |
| `catalog_spell_types` | All spell types |
| `catalog_powers` | All possible power values |
| `catalog_toughnesses` | All possible toughness values |
| `catalog_loyalties` | All possible loyalty values |
| `catalog_keyword_abilities` | All keyword abilities |
| `catalog_keyword_actions` | All keyword actions |
| `catalog_ability_words` | All ability words |
| `catalog_supertypes` | All supertypes |

### Bulk Data & Migrations (2)
| Tool | Description |
|---|---|
| `list_bulk_data` | List available bulk data downloads |
| `list_migrations` | List card-object migration records |

### Server Info (1)
| Tool | Description |
|---|---|
| `get_server_info` | Shows included/excluded fields and tools with descriptions |

## Card Fields Returned

Card responses include these fields only:

**Identity:** `id`, `oracle_id`, `tcgplayer_id`, `name`, `layout`, `released_at`, `uri`, `rulings_uri`

**Gameplay:** `mana_cost`, `cmc`, `type_line`, `oracle_text`, `power`, `toughness`, `loyalty`, `defense`, `life_modifier`, `hand_modifier`, `colors`, `color_identity`, `color_indicator`, `keywords`, `produced_mana`, `all_parts`, `card_faces`, `legalities`, `games`, `reserved`

**Print:** `set`, `set_name`, `set_type`, `rarity`, `digital`, `flavor_name`, `reprint`, `variation`, `variation_of`

**Price:** `prices.usd`

All other fields are stripped to save context window space. Call `get_server_info` to see exactly what's excluded and why you might want to add it.

## Adding Fields or Tools Later

1. Edit `metadata.py` to move entries between `INCLUDED_FIELDS` / `EXCLUDED_FIELDS` or `INCLUDED_TOOLS` / `EXCLUDED_TOOLS`
2. For new tools, add the endpoint method in `scryfall_client.py` and the `@mcp.tool()` function in `server.py`
3. Restart the server

## Scryfall API Usage

This server uses the [Scryfall API](https://scryfall.com/docs/api) which is free and requires no API key. Please respect their rate limits and terms of use. The server enforces a 100ms minimum delay between requests.

## License

This project is for personal use. Scryfall data is provided under Scryfall's terms. Card names, Oracle text, and other game content are property of Wizards of the Coast.
