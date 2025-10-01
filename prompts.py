
def main_prompt(language, genre_text):
    """
    Generates a detailed prompt for the Gemini AI to suggest a song based on an image.

    Args:
        language (str): The desired language for the song suggestion.
        genre_text (str): A formatted string specifying the genre preference.

    Returns:
        str: The complete, detailed prompt for the AI.
    """
    song_sugg_prompt = f"""You are an expert music curator for social media. Your task is to analyze the provided image and suggest a single song that perfectly matches its vibe for an Instagram story.

**Image Analysis:**
1.  **Mood & Vibe:** What is the overall feeling of the image (e.g., happy, melancholic, energetic, romantic, peaceful)?
2.  **Context:** What is happening in the image? Is it a landscape, a portrait, an event, a candid moment?
3.  **Visuals:** Note the colors, lighting, and composition. Are they bright and vibrant, or dark and moody?

**Song Suggestion Criteria:**
*   **Relevance:** The song's mood, tempo, and lyrics should align with the image's atmosphere.
*   **Instagram Story Fit:** The song should be engaging and suitable for a short video format.

Based on your analysis, provide one song suggestion. The song must be in **{language}**. {genre_text}

Your response must include:
1. Song_title: The title of the recommended song
2. Artist: The artist who performed the song
3. Summary: A concise paragraph (2-3 sentences) explaining what you analyzed in the image and why this specific song matches the image's mood, context, and visual elements.

Format your response as valid JSON with these three fields.
"""
    return song_sugg_prompt