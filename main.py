import requests
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import base64
import time
import webbrowser
import json
from typing import Optional, Dict, Any
import logging
from promtps import main_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Song(BaseModel):
    """Pydantic model for song data."""
    Song_title: str
    Artist: str

class Spotify:
    """Spotify API client for searching and retrieving track information."""
    
    # Constants
    TOKEN_DURATION = 45 * 60  # 45 minutes in seconds
    AUTH_URL = "https://accounts.spotify.com/api/token"
    SEARCH_URL = "https://api.spotify.com/v1/search"
    
    def __init__(self,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None) -> None:
        """Initialize Spotify client with credentials.
        
        Args:
            client_id: Spotify client ID (defaults to env variable)
            client_secret: Spotify client secret (defaults to env variable)
            
        Raises:
            ValueError: If credentials are not provided
        """
        self.token: Optional[str] = None
        self.token_expires_at: float = 0  # Timestamp when token expires
        
        # Use provided credentials or fallback to environment variables
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify client ID and secret are required. "
                           "Provide them as parameters or set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables.")
            
        self.auth_str = f"{self.client_id}:{self.client_secret}"
        self.b64_auth_str = base64.b64encode(self.auth_str.encode()).decode()

        # Generate token on initialization
        self._generate_token()

    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid (not expired).
        
        Returns:
            bool: True if token exists and is not expired, False otherwise
        """
        return self.token is not None and time.time() < self.token_expires_at

    def _generate_token(self) -> None:
        """Generate a new access token from Spotify API.
        
        Raises:
            requests.RequestException: If API request fails
            ValueError: If response doesn't contain access token
        """
        try:
            response = requests.post(
                self.AUTH_URL,
                headers={"Authorization": f"Basic {self.b64_auth_str}"},
                data={"grant_type": "client_credentials"},
                timeout=30  # Add timeout for better reliability
            )
            response.raise_for_status()

            response_data = response.json()
            if "access_token" not in response_data:
                raise ValueError("No access token in response from Spotify API")
                
            self.token = response_data["access_token"]
            self.token_expires_at = time.time() + self.TOKEN_DURATION
            logger.info("New Spotify access token generated successfully")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Spotify access token: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from Spotify API: {e}")
            raise

    def _ensure_valid_token(self) -> None:
        """Ensure we have a valid token, generate new one if expired."""
        if not self._is_token_valid():
            logger.info("Spotify token expired or invalid, generating new token...")
            self._generate_token()

    def search_track(self, track_name: str, artist_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for a track on Spotify.
        
        Args:
            track_name: Name of the track to search for
            artist_name: Optional artist name to narrow search
            
        Returns:
            Dict containing track information or None if not found
            
        Raises:
            ValueError: If track_name is empty
        """
        if not track_name.strip():
            raise ValueError("Track name cannot be empty")
            
        # Ensure we have a valid token before making the request
        self._ensure_valid_token()

        if artist_name:
            query = f"track:{track_name.strip()} artist:{artist_name.strip()}"
        else:
            query = f"track:{track_name.strip()}"
            
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"q": query, "type": "track", "limit": 1}

        try:
            response = requests.get(self.SEARCH_URL, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            tracks = data.get("tracks", {}).get("items", [])
            if tracks:
                track = tracks[0]
                return {
                    "id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"] if track.get("artists") else "Unknown",
                    "preview_url": track.get("preview_url"),
                    "spotify_url": track["external_urls"]["spotify"]
                }
            else:
                logger.info(f"No tracks found for query: {query}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for track '{track_name}': {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing track data for '{track_name}': {e}")
            return None

class Gemini:
    """Google Gemini AI client for image analysis and song suggestion."""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize Gemini client with API key.
        
        Args:
            api_key: Google API key (defaults to env variable)
            
        Raises:
            ValueError: If API key is not provided
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API key is required. "
                           "Provide it as parameter or set GOOGLE_API_KEY environment variable.")

        self.client = self._initialize_client()

    def _initialize_client(self) -> genai.Client:
        """Initialize the Gemini AI client.
        
        Returns:
            Configured Gemini AI client
            
        Raises:
            Exception: If client initialization fails
        """
        try:
            client = genai.Client(
                vertexai=False,
                api_key=self.api_key
            )
            logger.info("Gemini AI client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Could not initialize Gemini client: {e}")
            raise

    def _read_image_bytes(self, image_path: str) -> bytes:
        """Read image file as bytes.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image data as bytes
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            IOError: If file cannot be read
        """
        if not image_path:
            raise ValueError("Image path cannot be empty")
            
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            if not image_data:
                raise IOError(f"Image file is empty: {image_path}")
                
            return image_data
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            raise
        except IOError as e:
            logger.error(f"Error reading image file {image_path}: {e}")
            raise

    

    def song_title_gen(self, image_path: str, language: str = "English", genre:str="Asthetic") -> str:
        """Generate song suggestion based on image analysis.
        
        Args:
            image_path: Path to the image file
            language: Language preference for the song (default: English)
            genre: Optional genre preference
            
        Returns:
            JSON string containing song suggestion
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If AI generation fails
        """
        try:
            # Build prompt based on parameters
            genre_text = f"The preferred genre is {genre}." if genre else ""
            prompt = main_prompt(language, genre_text)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=self._read_image_bytes(image_path),
                        mime_type='image/png'
                    ),
                    prompt
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Song
                }
            )

            if not response.text:
                raise ValueError("Empty response from Gemini AI")
                
            logger.info(f"Song suggestion generated for image: {image_path}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating song suggestion for {image_path}: {e}")
            raise
        



def main(image_path, language, genre) -> None:
    """Main function to demonstrate the song suggestion workflow."""
    try:
        # Initialize AI client
        logger.info("Initializing Gemini AI client...")
        gemini_client = Gemini()
        
        # Configure image and preferences
        image_path = image_path
        language = "English" if not language else language
        genre = genre
        
        # Generate song suggestion
        logger.info(f"Generating song suggestion for image: {image_path}")
        song_json = gemini_client.song_title_gen(image_path, language=language, genre=genre)
        
        print(f"\nAI Song Suggestion:\n{song_json}\n")
        print("=" * 50)
        print("SEARCHING FOR SONG ON SPOTIFY...")
        print("=" * 50)

        # Parse song data and search on Spotify
        try:
            song_data = json.loads(song_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse song data: {e}")
            return
            
        track_title = song_data.get("Song_title")
        artist_name = song_data.get("Artist")
        
        if not track_title or not artist_name:
            logger.error("Invalid song data: missing title or artist")
            return

        # Initialize Spotify client and search
        logger.info("Initializing Spotify client...")
        spotify_client = Spotify()
        
        logger.info(f"Searching for track: '{track_title}' by '{artist_name}'")
        track_info = spotify_client.search_track(track_title, artist_name)
        
        if track_info:
            print(f"\nSpotify Track Found:")
            print(f"Title: {track_info['name']}")
            print(f"Artist: {track_info['artist']}")
            print(f"Spotify URL: {track_info['spotify_url']}")
            
            # Ask user if they want to open in browser
            user_choice = input("\nOpen song in browser? (y/n): ").strip().lower()
            if user_choice in ['y', 'yes']:
                webbrowser.open(track_info['spotify_url'])
                logger.info("Opened song in browser")
            else:
                print(f"\nYou can manually open: {track_info['spotify_url']}")
        else:
            logger.warning(f"No Spotify track found for '{track_title}' by '{artist_name}'")
            print("\nSorry, couldn't find this song on Spotify. Try searching manually.")
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main(
        r"D:\AI_coding\ig_song_suggestion\python_spotify\image.png",
        language="hindi",
        genre="bollywood"
    )



    

    



