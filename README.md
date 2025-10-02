# Vibecheck 🎵 - AI-Powered Song Suggestor for Instagram

A modern web application that analyzes your images using AI and suggests perfect songs for your Instagram stories. Upload any photo, choose your vibe, and get personalized song recommendations with Spotify integration and Instagram story preview.

**Live Demo:** [Vibecheck](https://song-suggestor-rosy.vercel.app)

## ✨ Features

### Core Functionality
- **AI-Powered Image Analysis** - Uses Google Gemini AI to understand image context, mood, and atmosphere
- **🆕 Google Search Grounding** - Real-time web search to find currently trending songs on Instagram and social media
- **Creative & Accurate** - Higher creativity (temperature 0.7) balanced with search-based accuracy
- **Multiple Song Suggestions** - Get 3 curated song recommendations for each image
- **Spotify Integration** - Direct links to songs on Spotify with preview capability
- **Instagram Story Mockup** - Preview how your photo will look with the song overlay on your IG story
- **Multi-Language Support** - 10+ languages including English, Hindi, Punjabi, Spanish, Korean, Japanese, and more
- **Genre Customization** - Choose from 10+ mood categories (Pop, Romantic, Chill, Indie, Bollywood, etc.)
- **Context-Aware** - Add optional context (e.g., "sunset with friends") for more accurate suggestions
- **Trend-Aware** - Searches for songs trending NOW in October 2025 on Instagram, TikTok, and streaming platforms

### User Experience
- **Beautiful Modern UI** - Responsive design with smooth animations and gradient backgrounds
- **Mobile-First Design** - Optimized for mobile devices with swipe gestures
- **Real-Time Preview** - See your uploaded image instantly before processing
- **Loading States** - Engaging loading animations while AI generates suggestions
- **Error Handling** - Graceful fallbacks with Google search links if Spotify track not found

## 🚀 Tech Stack

### Frontend
- **HTML5/CSS3** - Modern, responsive design with CSS Grid and Flexbox
- **Vanilla JavaScript** - Clean, efficient frontend logic
- **Google Fonts** - Inter and Space Grotesk for beautiful typography

### Backend
- **FastAPI** - High-performance Python web framework
- **Google Gemini 2.0 Flash** - Latest AI model with advanced image analysis and song suggestion
- **Google Search Grounding** - Real-time web search integration for trending song discovery
- **Spotify Web API** - Music search and track information
- **Uvicorn** - ASGI server for production deployment

### APIs & Services
- **Google Generative AI (Gemini)** - Image understanding and song generation
- **Spotify API** - Track search, preview URLs, and metadata
- **Vercel** - Frontend hosting and deployment
- **Railway** - Backend API deployment

## 📁 Project Structure

```
python_spotify/
├── api.py                  # FastAPI backend server with endpoints
├── main.py                 # Core logic: Gemini AI and Spotify clients
├── prompts.py              # AI prompt templates for song generation
├── requirements.txt        # Python dependencies
├── Procfile               # Railway deployment configuration
├── static/                # Frontend assets
│   ├── index.html         # Main web page
│   ├── styles.css         # Styling and animations
│   └── app.js             # Client-side JavaScript
├── uploads/               # Temporary storage for uploaded images
└── tests_static/          # Sample images for testing
```

## 🛠️ Getting Started

### Prerequisites
- **Python 3.10+**
- **Google API Key** (for Gemini AI)
- **Spotify Developer Account** (for API credentials)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RishabhBansal22/song-suggestor.git
   cd python_spotify
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

4. **Get API credentials:**
   - **Google Gemini:** Visit [Google AI Studio](https://aistudio.google.com/apikey) to get your API key
   - **Spotify:** Create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

### Running Locally

#### Option 1: Run the Web App (Recommended)
```bash
# Start the FastAPI server
python api.py

# Access the app at http://localhost:8080
```

#### Option 2: Run as CLI Script
```bash
# Edit main.py to set your image path and preferences
python main.py
```

### Deployment

The app is designed for easy deployment:
- **Frontend:** Deploy `static/` folder to Vercel, Netlify, or any static host
- **Backend:** Deploy to Railway, Render, or Heroku using the included `Procfile`

## 🎯 How to Use

1. **Upload Your Photo** - Drag & drop or browse to select an image
2. **Choose Language** - Select your preferred song language (English, Hindi, etc.)
3. **Pick Your Vibe** - Choose a mood/genre (Pop, Romantic, Chill, etc.)
4. **Add Context** (Optional) - Describe what's in the image for better results
5. **Get Suggestions** - Click "Get My Song" and wait for AI magic
6. **Preview & Share** - See your Instagram story mockup and access songs on Spotify

## 📝 API Endpoints

### `POST /suggest-song`
Generate song suggestions based on image analysis.

**Request:**
- **Form Data:**
  - `image` (File): Image file to analyze
  - `language` (String): Preferred language (default: "English")
  - `genre` (String): Mood/genre preference (default: "Popular")
  - `context` (String, Optional): Additional context about the image

**Response:**
```json
{
  "songs": [
    {
      "song_title": "Perfect",
      "artist": "Ed Sheeran",
      "spotify_url": "https://open.spotify.com/track/...",
      "preview_url": "https://p.scdn.co/mp3-preview/...",
      "spotify_id": "0tgVpDi06FyKpA1z0VMD4v",
      "google_search_url": "https://www.google.com/search?q=...",
      "spotify_error": false
    }
  ]
}
```

### `GET /health`
Health check endpoint to verify API status.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- Add more language options
- Improve AI prompts for better song matching
- Add playlist creation feature
- Implement user accounts and history
- Add more social media platform support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Rishabh Bansal**
- GitHub: [@RishabhBansal22](https://github.com/RishabhBansal22)
- Project Link: [https://github.com/RishabhBansal22/song-suggestor](https://github.com/RishabhBansal22/song-suggestor)

## 🙏 Acknowledgments

- Google Gemini AI for powerful image analysis
- Spotify Web API for music data and previews
- FastAPI for the excellent web framework
- All contributors and users of this project

---

Made with ❤️ for Instagram creators who want the perfect soundtrack for their stories ✨
