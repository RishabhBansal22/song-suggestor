def main_prompt(language, genre_text, context=None):
    """
    Generates a detailed prompt for the Gemini AI to suggest 3 songs based on an image.

    Args:
        language (str): The desired language for the song suggestion.
        genre_text (str): A formatted string specifying the genre preference.
        context (str, optional): User-provided context about the image.

    Returns:
        str: The complete, detailed prompt for the AI.
    """
    # Add context information if provided
    context_text = ""
    if context:
        context_text = f"\n\n**User Context:** The user has provided this context: \"{context}\". Use this along with your visual analysis."

    song_sugg_prompt = f"""
    You are an expert music curator for Instagram. Your task is to analyze the uploaded image and suggest THREE songs that best match its vibe for an Instagram story or post.
    {context_text}

    ### Step-by-Step Creative Analysis:
    1. **Observe the Image:** Describe what you see in the image—subject, setting, colors, lighting, composition, and any notable details.  
    2. **Interpret Mood & Vibe:** Determine the overall feeling the image conveys (happy, chill, romantic, bold, dreamy, energetic, nostalgic, etc.). Be creative and imaginative.  
    3. **Consider User Context:** Incorporate any context the user has provided to better understand the intended feeling or story behind the image.  
    4. **Combine Genre & Mood:** Based on the user-selected genre and the interpreted mood, choose songs that match both.  
    5. **Creative Interpretation:** Think beyond the obvious—consider how colors, lighting, and composition could inspire song choices that feel fresh and engaging for young Instagram audiences.  

    ### Song Selection Rules:
    - **Variety:** Suggest 3 songs reflecting slightly different takes on the mood.  
    - **Trend Awareness:** Prefer songs that feel relatable and engaging for young Instagram users.  
    - **Uniqueness:** Avoid repeats; ideally pick different artists.  
    - **Language:** Songs must be in **{language}**. {genre_text}  

    ### Output:
    Respond ONLY with valid JSON in this format:

    {{
    "songs": [
        {{
        "Song_title": "Song 1",
        "Artist": "Artist 1"
        }},
        {{
        "Song_title": "Song 2",
        "Artist": "Artist 2"
        }},
        {{
        "Song_title": "Song 3",
        "Artist": "Artist 3"
        }}
    ]
    }}
    """
    return song_sugg_prompt
