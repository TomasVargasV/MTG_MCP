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
# SSE mode (default) — for Joule and HTTP clients
python server.py

# stdio mode — for Claude Desktop
python server.py --transport stdio
```

The server supports two transport modes:

| Flag | Default | Description |
|---|---|---|
| `--transport` | `sse` | `sse` for Joule / HTTP clients, `stdio` for Claude Desktop |
| `--host` | `127.0.0.1` | Host to bind to in SSE mode |
| `--port` | `8000` | Port to bind to in SSE mode |

A `start_server.bat` file is included for one-click startup on Windows (SSE mode on port 8000).

## Connecting to Joule Work Desktop

1. **Start the server** in SSE mode (the default):
   ```bash
   python server.py
   ```
   Or double-click `start_server.bat`. The server will listen on `http://127.0.0.1:8000`.

2. **In Joule**, click the **Extensions icon** (database icon in the left navigation rail) → **Connectors** tab.

3. Click **+ New** → **Add Connector**.

4. Enter:
   - **Name:** `Scryfall MTG`
   - **URL:** `http://127.0.0.1:8000/sse`

5. Click **Add**.

6. In your chat, open the **connector picker** (in the message input toolbar) and toggle **Scryfall MTG** on for the conversation.

> **Note:** The server must be running before Joule can connect. Start it before opening Joule or before activating the connector.

## Connecting to Claude Desktop

Claude Desktop uses stdio transport. Edit your config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "scryfall-mtg": {
      "command": "python",
      "args": ["C:/path/to/scryfall-mtg/server.py", "--transport", "stdio"],
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
      "args": ["C:/path/to/scryfall-mtg/server.py", "--transport", "stdio"],
      "env": {}
    }
  }
}
```

Restart Claude Desktop after saving.

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
