llm_instructions = """
Create a playlist of songs to enhance the experience of reading  with  the context bellow . 
Select tracks that match the book's tone, themes, and setting, ensuring a cohesive and immersive 
listening experience. Include a mix of genres and tempos to complement the narrative's mood, with a 
brief explanation of why each song fits the book and context.Incorporate a variety of tempos and moods within 
the {style} style to complement the narrative.
Provide a list of {min_songs}-{max_songs}
songs with artist names, song titles. The list also must have a name and a description.
Select tracks that align with the book's tone, themes, and setting, ensuring a cohesive and immersive listening experience.
Here is the context to create a playlist:
Book: {book_info}
Category: {category}
Summary:
{context}
"""

styles = {
    "Any Style": "A diverse mix of genres and tempos, adaptable to any book's tone, themes, or setting for a versatile reading experience.",
    "Classical": "Instrumental orchestral or solo piano pieces",
    "Ambient": "Atmospheric, minimalist soundscapes",
    "Cinematic Soundtrack": "Epic, orchestral scores",
    "Jazz": "Smooth or upbeat jazz",
    "Indie Folk": "Acoustic, heartfelt tunes",
    "Lo-Fi": "Chill, relaxed beats",
    "Electronic/Chillwave": "Synth-driven, dreamy tracks",
    "Acoustic": "Raw, guitar-driven songs and live songs",
    "World Music": "Culturally specific or global sounds",
    "Post-Rock": "Instrumental, emotive soundscapes",
    "Neo-Soul": "Soulful, mellow vibes",
    "Baroque": "Ornate, classical compositions",
    "Dark Academia": "Moody, classical, or gothic tones",
    "Retro/Vintage": "Nostalgic tracks (e.g., 60s/70s pop or rock)",
    "Epic Fantasy": "Grand, mythical, or orchestral music",
}
