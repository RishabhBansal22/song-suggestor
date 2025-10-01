from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
import logging
from pathlib import Path
from main import Gemini, Spotify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Song Suggestor API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for frontend
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Create uploads directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def create_google_search_url(song_title: str, artist: str) -> str:
    """Create a Google search URL for the given song and artist."""
    import urllib.parse
    query = f"{song_title} {artist} song"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

class SingleSongResponse(BaseModel):
    """Response model for a single song."""
    song_title: str
    artist: str
    summary: str
    spotify_url: str | None = None
    preview_url: str | None = None
    spotify_id: str | None = None
    google_search_url: str | None = None
    spotify_error: bool = False

class SongResponse(BaseModel):
    """Response model for multiple song suggestions."""
    songs: list[SingleSongResponse]

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Song Suggestor API is running! 🎵"}

@app.post("/suggest-song", response_model=SongResponse)
async def suggest_song(
    image: UploadFile = File(...),
    language: str = Form("English"),
    genre: str = Form("Popular"),
    context: str = Form(None)
):
    """
    Generate 3 song suggestions based on uploaded image.
    
    Args:
        image: Uploaded image file
        language: Preferred song language (default: English)
        genre: Preferred genre/vibe (default: Popular)
        context: Optional context about the image (e.g., "me with my brother")
    
    Returns:
        SongResponse with 3 songs, each with details and Spotify info
    """
    try:
        # Validate file type
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Save uploaded image temporarily
        file_extension = os.path.splitext(image.filename)[1]
        temp_file_path = UPLOAD_DIR / f"temp_{os.getpid()}{file_extension}"
        
        logger.info(f"Processing image: {image.filename}")
        logger.info(f"Language: {language}, Genre: {genre}")
        if context:
            logger.info(f"Context: {context}")
        
        # Write file to disk
        with open(temp_file_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        try:
            # Initialize Gemini AI client
            gemini_client = Gemini()
            
            # Generate song suggestions (3 songs)
            song_json = gemini_client.song_title_gen(
                str(temp_file_path),
                language=language,
                genre=genre,
                context=context
            )
            
            # Parse AI response
            songs_data = json.loads(song_json)
            song_list = songs_data.get("songs", [])
            
            if not song_list or len(song_list) == 0:
                raise ValueError("No songs returned from AI")
            
            # Initialize Spotify client once for all searches
            spotify_client = None
            try:
                spotify_client = Spotify()
            except Exception as e:
                logger.warning(f"Failed to initialize Spotify client: {e}")
            
            # Process each song with individual error handling
            processed_songs = []
            for idx, song_data in enumerate(song_list):
                track_title = song_data.get("Song_title")
                artist_name = song_data.get("Artist")
                summary = song_data.get("Summary", "")
                
                if not track_title or not artist_name:
                    logger.warning(f"Invalid song data for song {idx + 1}, skipping")
                    continue
                
                # Search on Spotify with error handling per song
                spotify_error = False
                track_info = None
                
                if spotify_client:
                    try:
                        track_info = spotify_client.search_track(track_title, artist_name)
                        logger.info(f"Song {idx + 1}: Found on Spotify - {track_title} by {artist_name}")
                    except Exception as e:
                        logger.warning(f"Spotify search failed for song {idx + 1} ({track_title}): {e}")
                        spotify_error = True
                else:
                    spotify_error = True
                
                # Create Google search URL as fallback
                google_search_url = create_google_search_url(track_title, artist_name)
                
                # Build song response
                song_response = {
                    "song_title": track_title,
                    "artist": artist_name,
                    "summary": summary,
                    "spotify_url": track_info.get("spotify_url") if track_info else None,
                    "preview_url": track_info.get("preview_url") if track_info else None,
                    "spotify_id": track_info.get("id") if track_info else None,
                    "google_search_url": google_search_url,
                    "spotify_error": spotify_error or track_info is None
                }
                
                processed_songs.append(song_response)
            
            if not processed_songs:
                raise ValueError("No valid songs could be processed")
            
            logger.info(f"Successfully processed {len(processed_songs)} songs")
            return {"songs": processed_songs}
            
        finally:
            # Clean up temporary file
            if temp_file_path.exists():
                temp_file_path.unlink()
                logger.info("Temporary file cleaned up")
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running smoothly ✨"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
