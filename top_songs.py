import sys
import os
import traceback
from typing import Any, List, Tuple
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import base64
import requests

class SpotifyAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize Spotify credentials
        self._init_spotify()

        # Initialize MCP Server
        self.mcp = FastMCP("spotify_top_tracks")
        print("MCP Server initialized", file=sys.stderr)

        # Register MCP tools
        self._register_tools()

    def _init_spotify(self):
        """Load and verify Spotify API credentials from environment."""
        try:
            self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
            self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
            if not self.client_id or not self.client_secret:
                raise ValueError("Missing Spotify client ID or secret in environment variables")
            print("Spotify credentials loaded successfully", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing Spotify credentials: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

    def _get_access_token(self) -> str:
        """Obtain an access token using the Client Credentials flow."""
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64 = base64.b64encode(auth_str.encode()).decode()
        try:
            resp = requests.post(
                "https://accounts.spotify.com/api/token",
                headers={
                    "Authorization": f"Basic {b64}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={"grant_type": "client_credentials"}
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
        except Exception as e:
            print(f"Error obtaining Spotify token: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    def _search_artist(self, token: str, artist_name: str) -> str:
        """Search for an artist and return its Spotify ID."""
        try:
            resp = requests.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": artist_name, "type": "artist", "limit": 1}
            )
            resp.raise_for_status()
            items = resp.json().get("artists", {}).get("items", [])
            if not items:
                raise ValueError(f"No artist found for '{artist_name}'")
            return items[0]["id"]
        except Exception as e:
            print(f"Error searching for artist '{artist_name}': {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    def _fetch_top_tracks(self, token: str, artist_id: str, market: str) -> List[Tuple[str, int]]:
        """Fetch top 5 tracks for the given artist ID."""
        try:
            resp = requests.get(
                f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
                headers={"Authorization": f"Bearer {token}"},
                params={"market": market}
            )
            resp.raise_for_status()
            tracks = resp.json().get("tracks", [])[:5]
            return [(t["name"], t["popularity"]) for t in tracks]
        except Exception as e:
            print(f"Error fetching top tracks for artist {artist_id}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    def _register_tools(self):
        """Register MCP tools for fetching Spotify top tracks."""
        @self.mcp.tool()
        async def get_top_tracks(artist_name: str, market: str = "US") -> List[Tuple[str, int]]:
            """Return the artist's top 5 tracks with their popularity."""
            print(f"Fetching top tracks for '{artist_name}' (market={market})", file=sys.stderr)
            try:
                token = self._get_access_token()
                artist_id = self._search_artist(token, artist_name)
                result = self._fetch_top_tracks(token, artist_id, market)
                print(f"Successfully fetched top tracks for '{artist_name}'", file=sys.stderr)
                return result
            except Exception as e:
                print(f"Failed to get top tracks: {e}", file=sys.stderr)
                return []

    def run(self):
        """Start the MCP server."""
        try:
            print("Running MCP Server for Spotify Top Tracks...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = SpotifyAnalyzer()
    analyzer.run()
