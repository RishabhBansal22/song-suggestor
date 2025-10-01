
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
        context_text = f"\n\n**User Context:** The user has provided this context about the image: \"{context}\". Consider this information along with your visual analysis."
    
    song_sugg_prompt = f"""You are an expert music curator for social media. Your task is to analyze the provided image and suggest THREE different songs that match its vibe for an Instagram story.

**Image Analysis:**
1.  **Mood & Vibe:** What is the overall feeling of the image (e.g., happy, melancholic, energetic, romantic, peaceful)?
2.  **Context:** What is happening in the image? Is it a landscape, a portrait, an event, a candid moment?
3.  **Visuals:** Note the colors, lighting, and composition. Are they bright and vibrant, or dark and moody?{context_text}

**Song Suggestion Criteria:**
*   **Relevance:** Each song's mood, tempo, and lyrics should align with the image's atmosphere.
*   **Variety:** Provide 3 DIFFERENT songs with slightly varied interpretations of the image's mood (e.g., one upbeat, one mellow, one intense).
*   **Instagram Story Fit:** All songs should be engaging and suitable for a short video format.
*   **No Duplicates:** Ensure all 3 songs are unique and from different artists if possible.

Based on your analysis, provide THREE song suggestions. All songs must be in **{language}**. {genre_text}

Your response must be a JSON object with a "songs" array containing 3 song objects. Each song object must include:
1. Song_title: The title of the recommended song
2. Artist: The artist who performed the song

**IMPORTANT:** Return exactly 3 songs, each offering a slightly different mood interpretation while matching the overall image vibe.

Format your response as valid JSON with the structure: {{"songs": [{{Song_title, Artist}}, {{Song_title, Artist}}, {{Song_title, Artist}}]}}
"""
    return song_sugg_prompt