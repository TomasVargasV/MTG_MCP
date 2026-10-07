"""
HTTP client for the Scryfall API.

Handles:
- Rate limiting (max 10 requests per second, as per Scryfall guidelines)
- Field filtering on card objects
- Error handling
- Multi-face card handling
"""

import asyncio
import time
from typing import Any

import httpx

from metadata import INCLUDED_FIELD_KEYS

BASE_URL = "https://api.scryfall.com"

# Scryfall asks for max 10 req/s for the general API, but specific endpoints
# like /cards/search and /cards/collection are limited to 2 req/s.
# We use a conservative 100ms delay between all requests.
MIN_REQUEST_INTERVAL = 0.1  # seconds


class ScryfallClient:
    """Async HTTP client for the Scryfall API with rate limiting and field filtering."""

    def __init__(self) -> None:
        self._last_request_time: float = 0.0
        self._lock = asyncio.Lock()
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers={
                    "User-Agent": "ScryfallMCPServer/1.0",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _rate_limit(self) -> None:
        """Enforce minimum interval between requests."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < MIN_REQUEST_INTERVAL:
                await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
            self._last_request_time = time.monotonic()

    async def _request(
        self,
        method: str,
        path: str,
        params: dict = None,
        json_body: dict = None,
    ) -> dict:
        """Make a rate-limited request to the Scryfall API."""
        await self._rate_limit()
        client = await self._get_client()

        try:
            if method == "GET":
                response = await client.get(path, params=params)
            elif method == "POST":
                response = await client.post(path, json=json_body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 404:
                return {
                    "error": True,
                    "status": 404,
                    "details": "Not found. The requested resource does not exist on Scryfall.",
                }

            if response.status_code == 422:
                data = response.json()
                return {
                    "error": True,
                    "status": 422,
                    "details": data.get("details", "Bad request."),
                }

            if response.status_code == 429:
                return {
                    "error": True,
                    "status": 429,
                    "details": "Rate limited by Scryfall. Please wait a moment and try again.",
                }

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status": e.response.status_code,
                "details": str(e),
            }
        except httpx.RequestError as e:
            return {"error": True, "status": 0, "details": f"Network error: {e}"}

    # ------------------------------------------------------------------
    # Field filtering
    # ------------------------------------------------------------------

    def filter_card(self, card: dict) -> dict:
        """Strip a card object to only the included fields."""
        filtered = {}

        for key in INCLUDED_FIELD_KEYS:
            if key in card:
                filtered[key] = card[key]

        # Special handling for prices: only keep prices.usd
        if "prices" in card and isinstance(card["prices"], dict):
            filtered["prices"] = {"usd": card["prices"].get("usd")}

        # Special handling for card_faces: filter each face too
        if "card_faces" in card and isinstance(card["card_faces"], list):
            filtered["card_faces"] = [
                self._filter_card_face(face) for face in card["card_faces"]
            ]

        return filtered

    def _filter_card_face(self, face: dict) -> dict:
        """Filter a card face object to gameplay-relevant fields."""
        face_fields = {
            "name", "mana_cost", "type_line", "oracle_text",
            "power", "toughness", "loyalty", "defense",
            "colors", "color_indicator", "flavor_name",
        }
        return {k: v for k, v in face.items() if k in face_fields}

    def filter_card_list(self, data: dict) -> dict:
        """Filter a Scryfall list response containing card objects."""
        if data.get("error"):
            return data

        result = {"object": "list"}

        if "total_cards" in data:
            result["total_cards"] = data["total_cards"]
        if "has_more" in data:
            result["has_more"] = data["has_more"]

        if "data" in data and isinstance(data["data"], list):
            result["data"] = [self.filter_card(card) for card in data["data"]]

        return result

    # ------------------------------------------------------------------
    # Card endpoints
    # ------------------------------------------------------------------

    async def search_cards(
        self,
        query: str,
        unique: str = "cards",
        order: str = "name",
        direction: str = "auto",
        page: int = 1,
    ) -> dict:
        """GET /cards/search"""
        params = {
            "q": query,
            "unique": unique,
            "order": order,
            "dir": direction,
            "page": page,
        }
        data = await self._request("GET", "/cards/search", params=params)
        return self.filter_card_list(data)

    async def get_card_by_name(
        self, name: str, fuzzy: bool = True, set_code: str = None
    ) -> dict:
        """GET /cards/named"""
        params = {}
        if fuzzy:
            params["fuzzy"] = name
        else:
            params["exact"] = name
        if set_code:
            params["set"] = set_code
        data = await self._request("GET", "/cards/named", params=params)
        if data.get("error"):
            return data
        return self.filter_card(data)

    async def autocomplete_card_name(self, query: str) -> dict:
        """GET /cards/autocomplete"""
        params = {"q": query}
        # Autocomplete returns names, not card objects. No filtering needed.
        return await self._request("GET", "/cards/autocomplete", params=params)

    async def get_card_collection(self, identifiers: list) -> dict:
        """POST /cards/collection"""
        body = {"identifiers": identifiers}
        data = await self._request("POST", "/cards/collection", json_body=body)
        return self.filter_card_list(data)

    async def get_card_by_id(self, scryfall_id: str) -> dict:
        """GET /cards/:id"""
        data = await self._request("GET", f"/cards/{scryfall_id}")
        if data.get("error"):
            return data
        return self.filter_card(data)

    async def get_card_by_set(self, set_code: str, collector_number: str) -> dict:
        """GET /cards/:code/:number"""
        data = await self._request("GET", f"/cards/{set_code}/{collector_number}")
        if data.get("error"):
            return data
        return self.filter_card(data)

    async def get_card_by_cardmarket(self, cardmarket_id: int) -> dict:
        """GET /cards/cardmarket/:id"""
        data = await self._request("GET", f"/cards/cardmarket/{cardmarket_id}")
        if data.get("error"):
            return data
        return self.filter_card(data)

    # ------------------------------------------------------------------
    # Rulings
    # ------------------------------------------------------------------

    async def get_rulings_by_id(self, scryfall_id: str) -> dict:
        """GET /cards/:id/rulings"""
        return await self._request("GET", f"/cards/{scryfall_id}/rulings")

    async def get_rulings_by_set(self, set_code: str, collector_number: str) -> dict:
        """GET /cards/:code/:number/rulings"""
        return await self._request(
            "GET", f"/cards/{set_code}/{collector_number}/rulings"
        )

    # ------------------------------------------------------------------
    # Sets
    # ------------------------------------------------------------------

    async def list_sets(self) -> dict:
        """GET /sets"""
        return await self._request("GET", "/sets")

    async def get_set(self, set_code: str) -> dict:
        """GET /sets/:code"""
        return await self._request("GET", f"/sets/{set_code}")

    # ------------------------------------------------------------------
    # Symbology
    # ------------------------------------------------------------------

    async def list_symbols(self) -> dict:
        """GET /symbology"""
        return await self._request("GET", "/symbology")

    async def parse_mana_cost(self, cost: str) -> dict:
        """GET /symbology/parse-mana"""
        return await self._request(
            "GET", "/symbology/parse-mana", params={"cost": cost}
        )

    # ------------------------------------------------------------------
    # Catalogs
    # ------------------------------------------------------------------

    async def get_catalog(self, catalog_name: str) -> dict:
        """GET /catalog/:name"""
        return await self._request("GET", f"/catalog/{catalog_name}")

    # ------------------------------------------------------------------
    # Bulk data
    # ------------------------------------------------------------------

    async def list_bulk_data(self) -> dict:
        """GET /bulk-data"""
        return await self._request("GET", "/bulk-data")

    # ------------------------------------------------------------------
    # Migrations
    # ------------------------------------------------------------------

    async def list_migrations(self) -> dict:
        """GET /migrations"""
        return await self._request("GET", "/migrations")
