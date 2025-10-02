# Grounding Query Improvements

## Problem Identified
The model was generating **generic grounding queries** that only considered language and genre:
```
❌ Bad queries:
- 'trending hindi indie songs october 2025 instagram tiktok'
- 'most popular hindi indie songs 2025'
- 'top hindi indie artists 2025'
```

These queries ignored the **image content** entirely, resulting in generic song suggestions that didn't match the specific mood, setting, or vibe of the photo.

---

## Solution Implemented

### 1. **Enhanced Prompt Structure** (`prompts.py`)
Added a **3-step workflow** to the grounding prompt:

#### STEP 1: Analyze the Image
- Extract mood/emotion (happy, melancholic, energetic, peaceful, romantic)
- Identify setting (beach, city, nature, indoor, party, travel)
- Recognize activity/theme (celebration, relaxation, adventure, friendship)
- Note lighting/colors (golden hour, neon lights, dark and moody, bright)
- Capture overall aesthetic (vintage, modern, minimalist, cinematic)

#### STEP 2: Generate Context-Rich Search Queries
Combine multiple elements:
- Language and genre: "hindi indie"
- **Image-specific mood**: "romantic", "energetic", "melancholic"
- **Visual setting**: "beach vibes", "city night", "road trip"
- Trending context: "october 2025 instagram tiktok"

#### STEP 3: Match Songs to Specific Context
- Return songs that match BOTH trending status AND the specific image vibe
- Ensure diversity (different artists)
- Verify language and genre requirements

### 2. **Improved System Instructions** (`main.py`)
Enhanced the system instruction with:
- Clear workflow steps emphasizing image analysis first
- Examples of GOOD vs BAD search queries
- Explicit requirement to incorporate visual analysis in queries
- Emphasis on matching specific mood, not just general trends

---

## Expected Results

### Before:
```
Image: Beach sunset with couple
Queries: 
- "trending hindi indie songs october 2025"
- "popular hindi indie 2025"

Result: Generic indie songs, not matching the romantic beach sunset vibe
```

### After:
```
Image: Beach sunset with couple
Queries:
- "trending hindi romantic beach sunset golden hour songs october 2025 instagram"
- "popular hindi love songs ocean vibes 2025 tiktok"
- "viral hindi romantic coastal evening songs october 2025"

Result: Specific romantic, beach-themed songs that match the visual mood
```

---

## Benefits

1. **Contextual Relevance**: Songs now match the specific image mood and setting
2. **Better User Experience**: Suggestions feel personalized and thoughtful
3. **Improved Search Quality**: More specific queries = better grounding results
4. **Visual-Audio Harmony**: Songs complement the visual aesthetic of the image

---

## Testing Recommendations

Test with diverse images to verify query generation:
- **Energetic party scene** → Should query for "party anthem", "celebration", "dance"
- **Melancholic rainy photo** → Should query for "sad", "rainy day", "melancholic"
- **Travel/adventure** → Should query for "road trip", "adventure", "wanderlust"
- **Romantic couple** → Should query for "romantic", "love", "couple"
- **City nightlife** → Should query for "city night", "urban", "neon lights"

Monitor the logged `web_search_queries` to ensure they now include image-specific context.
