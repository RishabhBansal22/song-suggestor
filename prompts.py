def main_prompt(language, genre_text, context=None, use_grounding=True):
    """
    Generates a concise prompt for the Gemini AI to suggest 3 songs based on an image.

    Args:
        language (str): The desired language for the song suggestion.
        genre_text (str): A formatted string specifying the genre preference.
        context (str, optional): User-provided context about the image.
        use_grounding (bool): Whether Google Search grounding is available.

    Returns:
        str: A concise, focused prompt for the AI.
    """
    context_text = f"\n\nUser context: {context}" if context else ""
    
    # Different prompts based on whether grounding is available
    if use_grounding:
        # Prompt for when Google Search grounding is available
        song_sugg_prompt = f"""STEP 1 - ANALYZE THE IMAGE:
First, carefully examine this image and identify:
- Primary mood/emotion (happy, melancholic, energetic, peaceful, romantic, etc.)
- Visual setting (beach, city, nature, indoor, party, travel, etc.)
- Activity or theme (celebration, relaxation, adventure, friendship, love, etc.)
- Lighting and colors (golden hour, neon lights, dark and moody, bright and vibrant, etc.)
- Overall vibe/aesthetic (vintage, modern, minimalist, cinematic, candid, etc.)

STEP 2 - USE GOOGLE SEARCH TO FIND MATCHING SONGS:
Based on your image analysis, use Google Search to find trending {language} songs that match these specific visual characteristics.

When searching, combine:
1. The language: "{language}"
2. The image's specific mood/vibe you identified (e.g., "romantic", "energetic", "melancholic")
3. The setting/theme (e.g., "beach vibes", "city night", "road trip")
4. Current trends: "october 2025 instagram tiktok trending"

Example search queries you should generate:
- "trending {language} romantic beach songs instagram"
- "popular {language} energetic party anthems tiktok"
- "viral {language} melancholic indie songs 2025"

STEP 3 - PROVIDE RESULTS:
Suggest 3 different songs by different artists that:
- Match the SPECIFIC mood and setting you identified in the image
- Are currently trending on Instagram/TikTok (based on your search)
- Are in {language} language
- Fit the appropriate genre based on the image's vibe

Provide exact song titles and artist names.{context_text}"""
    else:
        # Prompt for fallback without grounding (rely on training data)
        song_sugg_prompt = f"""Analyze this image and suggest 3 songs for an Instagram story that match its mood and vibe.{context_text}

Requirements:
- All songs MUST be in {language} language
- Match the genre to the image's mood and atmosphere
- Suggest popular, well-known songs that fit the vibe
- Provide exact song titles and artist names
- Each song should be by a different artist

Consider the image's colors, lighting, mood, setting, and emotional atmosphere when choosing songs."""
    
    return song_sugg_prompt
