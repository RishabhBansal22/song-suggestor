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
import mimetypes
from typing import Optional, Dict, Any
import logging
from prompts import main_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Song(BaseModel):
    """Pydantic model for song data."""
    Song_title: str
    Artist: str

class Songs(BaseModel):
    """Pydantic model for multiple song suggestions."""
    songs: list[Song]  # List of 3 song suggestions

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

        # Try multiple search strategies for better results
        search_queries = []
        
        if artist_name:
            # Strategy 1: Use only the first artist if multiple artists are present
            if ',' in artist_name:
                first_artist = artist_name.split(',')[0].strip()
                search_queries.append(f"track:{track_name.strip()} artist:{first_artist}")
                logger.info(f"Multiple artists detected, using first artist: {first_artist}")
            else:
                search_queries.append(f"track:{track_name.strip()} artist:{artist_name.strip()}")
            
            # Strategy 2: Search with track name and full artist string (without field specifiers)
            search_queries.append(f"{track_name.strip()} {artist_name.strip()}")
            
            # Strategy 3: Search with track name only as fallback
            search_queries.append(f"track:{track_name.strip()}")
        else:
            search_queries.append(f"track:{track_name.strip()}")
            
        headers = {"Authorization": f"Bearer {self.token}"}

        # Try each search strategy until we find a result
        for query in search_queries:
            params = {"q": query, "type": "track", "limit": 1}
            
            try:
                response = requests.get(self.SEARCH_URL, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                tracks = data.get("tracks", {}).get("items", [])
                if tracks:
                    track = tracks[0]
                    logger.info(f"Track found using query: {query}")
                    return {
                        "id": track["id"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"] if track.get("artists") else "Unknown",
                        "preview_url": track.get("preview_url"),
                        "spotify_url": track["external_urls"]["spotify"]
                    }
                else:
                    logger.info(f"No tracks found for query: {query}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error searching for track with query '{query}': {e}")
                continue
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing track data for query '{query}': {e}")
                continue
        
        # If all strategies failed
        logger.warning(f"All search strategies failed for track '{track_name}' by '{artist_name}'")
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
            
    def _detect_mime_type(self, image_path: str) -> str:
        """Detect MIME type of the image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detected MIME type as string
            
        Raises:
            ValueError: If MIME type cannot be detected
        """
        # Initialize mimetypes if needed
        if not mimetypes.inited:
            mimetypes.init()
            
        # Get MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(image_path)
        
        # If MIME type couldn't be detected from extension, try to determine by common image extensions
        if not mime_type:
            # Map common image extensions to MIME types
            extension_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            
            file_ext = os.path.splitext(image_path.lower())[1]
            mime_type = extension_map.get(file_ext)
            
        # Default to image/jpeg if we still couldn't determine the MIME type
        if not mime_type:
            logger.warning(f"Could not detect MIME type for {image_path}, defaulting to image/jpeg")
            mime_type = 'image/jpeg'
            
        logger.info(f"Detected MIME type for {image_path}: {mime_type}")
        return mime_type

    

    def song_title_gen(self, image_path: str, language: str = "English", genre: str = None, context: str = None) -> str:
        """Generate multiple song suggestions based on image analysis with multi-level fallback.
        
        Strategy:
        1. Try Google Search grounding with text output (most creative + trending)
        2. If JSON parsing fails, use structured output to convert
        3. If grounding fails entirely, fall back to normal structured output
        
        Args:
            image_path: Path to the image file
            language: Language preference for the song (default: English)
            genre: Optional genre preference (deprecated, kept for backward compatibility)
            context: Optional user-provided context about the image
            
        Returns:
            JSON string containing 3 song suggestions
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If all generation methods fail
        """
        # Build prompt and detect MIME type (genre is no longer used)
        genre_text = ""
        mime_type = self._detect_mime_type(image_path)
        image_bytes = self._read_image_bytes(image_path)
        
        # APPROACH 1: Try Google Search grounding (best for trending songs)
        try:
            logger.info("🔍 Attempting Google Search grounding for trending songs...")
            # Use grounding-enabled prompt
            prompt = main_prompt(language, genre_text, context, use_grounding=True)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    system_instruction="""You are an expert music curator for Instagram stories and reels.

YOUR WORKFLOW:
1. ANALYZE THE IMAGE: Identify mood, setting, activity, colors, and aesthetic
2. CRAFT SPECIFIC SEARCH QUERIES: Combine the visual analysis with language/genre to search for matching trending songs
   - Include image-specific context in queries (e.g., "beach sunset vibes", "city night energy", "melancholic rainy day")
   - Don't just search "trending hindi songs" - search "trending hindi romantic beach sunset songs october 2025"
3. SELECT PERFECT MATCHES: Choose songs that match BOTH the trending status AND the specific image vibe for young users.

CRITICAL:
- Your Google Search queries MUST incorporate the visual analysis from the image
- Match songs to the SPECIFIC emotional and visual mood of the image, not just general trends
- Always provide real, existing songs with accurate titles and artist names
- Return ONLY valid JSON with exactly 3 songs by different artists

Example of GOOD search query formation:
Image shows: Golden hour beach photo with couple
Search: "trending hindi romantic beach golden hour songs instagram"

Example of BAD search query:
Image shows: Golden hour beach photo with couple  
Search: "trending hindi songs october 2025" ❌ (too generic, missing image context)""",
                    tools=[{"google_search": {}}],
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2000,
                    candidate_count=1,
                )
            )

            if response.text:
                # Log grounding information
                try:
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                            grounding_meta = candidate.grounding_metadata
                            if hasattr(grounding_meta, 'web_search_queries') and grounding_meta.web_search_queries:
                                logger.info(f"   Search queries: {grounding_meta.web_search_queries}")
                            if hasattr(grounding_meta, 'grounding_chunks') and grounding_meta.grounding_chunks:
                                logger.info(f"   Grounded with {len(grounding_meta.grounding_chunks)} web sources")
                except Exception as meta_error:
                    logger.debug(f"Could not extract grounding metadata: {meta_error}")
                
                grounded_text = response.text
                logger.info(f"   Received grounded response ({len(grounded_text)} chars)")
                
                # APPROACH 2: Always use structured output to convert grounded text to JSON
                # (Skip JSON parsing as it frequently fails)
                try:
                    logger.info("🔄 Converting grounded response to JSON with structured output...")
                    structure_response = self.client.models.generate_content(
                        model="gemini-2.0-flash-001",
                        contents=f"""Extract song suggestions from this text as JSON with exactly 3 songs:

{grounded_text}""",
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=Songs,
                            temperature=0.1,
                        )
                    )
                    
                    if structure_response.text:
                        # Validate the structured response
                        validated = json.loads(structure_response.text)
                        if "songs" in validated and len(validated["songs"]) >= 3:
                            logger.info("✅ Successfully converted grounded response to JSON")
                            return structure_response.text
                except Exception as convert_error:
                    logger.warning(f"   Conversion failed: {convert_error}")
        
        except Exception as grounding_error:
            logger.warning(f"⚠️  Grounding approach failed: {grounding_error}")
        
        # APPROACH 3: Fallback to normal structured output (no grounding)
        try:
            logger.info("🔄 Falling back to standard structured output (no grounding)...")
            # Use non-grounding prompt (no mention of Google Search)
            fallback_prompt = main_prompt(language, genre_text, context, use_grounding=False)
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    fallback_prompt
                ],
                config=types.GenerateContentConfig(
                    system_instruction="""You are an expert music curator for Instagram.
Suggest songs that match the image's mood and vibe.
Provide real, existing songs with accurate titles and artist names.""",
                    response_mime_type="application/json",
                    response_schema=Songs,
                    temperature=0.5,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=800,
                )
            )
            
            if response.text:
                # Validate the response
                validated = json.loads(response.text)
                if "songs" in validated and len(validated["songs"]) >= 3:
                    logger.info("✅ Standard structured output successful")
                    return response.text
                else:
                    raise ValueError("Invalid song count in fallback response")
            else:
                raise ValueError("Empty response from fallback method")
                
        except Exception as fallback_error:
            logger.error(f"❌ All approaches failed. Last error: {fallback_error}")
            raise Exception(f"Failed to generate song suggestions after all attempts: {fallback_error}")
        



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
        
        # Log detected MIME type (for debugging purposes)
        mime_type = gemini_client._detect_mime_type(image_path)
        logger.info(f"Detected MIME type for input image: {mime_type}")
        
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
    # You can test with different image formats to ensure MIME type detection works correctly
    image_path = r"D:\AI_coding\ig_song_suggestion\python_spotify\tests_static\image.png"
    # Uncomment one of these to test other image formats:
    # image_path = r"D:\AI_coding\ig_song_suggestion\python_spotify\tests_static\mahak_udaiput.jpeg"
    # image_path = r"D:\AI_coding\ig_song_suggestion\python_spotify\tests_static\train_window.jpg"
    
    main(
        image_path,
        language="hindi",
        genre="bollywood"
    )









