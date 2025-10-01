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

class SongResponse(BaseModel):
    """Response model for song suggestions."""
    song_title: str
    artist: str
    summary: str
    spotify_url: str | None = None
    preview_url: str | None = None
    spotify_id: str | None = None
    google_search_url: str | None = None
    spotify_error: bool = False

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
    Generate song suggestion based on uploaded image.
    
    Args:
        image: Uploaded image file
        language: Preferred song language (default: English)
        genre: Preferred genre/vibe (default: Popular)
        context: Optional context about the image (e.g., "me with my brother")
    
    Returns:
        SongResponse with song details and Spotify info
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
            
            # Generate song suggestion
            song_json = gemini_client.song_title_gen(
                str(temp_file_path),
                language=language,
                genre=genre,
                context=context
            )
            
            # Parse AI response
            song_data = json.loads(song_json)
            track_title = song_data.get("Song_title")
            artist_name = song_data.get("Artist")
            summary = song_data.get("Summary", "")
            
            if not track_title or not artist_name:
                raise ValueError("Invalid song data from AI")
            
            # Search on Spotify with error handling
            spotify_error = False
            track_info = None
            
            try:
                spotify_client = Spotify()
                track_info = spotify_client.search_track(track_title, artist_name)
            except Exception as e:
                logger.warning(f"Spotify search failed: {e}")
                spotify_error = True
            
            # Create Google search URL as fallback
            google_search_url = create_google_search_url(track_title, artist_name)
            
            # Build response
            response_data = {
                "song_title": track_title,
                "artist": artist_name,
                "summary": summary,
                "spotify_url": track_info.get("spotify_url") if track_info else None,
                "preview_url": track_info.get("preview_url") if track_info else None,
                "spotify_id": track_info.get("id") if track_info else None,
                "google_search_url": google_search_url,
                "spotify_error": spotify_error or track_info is None
            }
            
            logger.info(f"Song suggestion generated: {track_title} by {artist_name}")
            return response_data
            
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
