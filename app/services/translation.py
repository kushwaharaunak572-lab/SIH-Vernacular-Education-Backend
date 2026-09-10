from deep_translator import MyMemoryTranslator


# Language name -> MyMemory language code
SUPPORTED_LANGUAGES = {
    "English": "en-GB",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Gujarati": "gu-IN",
    "Marathi": "mr-IN",
    "Punjabi": "pa-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Odia": "or-IN",
    "Assamese": "as-IN",
    "Nepali": "ne-NP",
    "Urdu": "ur-PK",
}


def translate_text(
    text: str,
    source_language: str,
    target_language: str
) -> str:

    # Empty text check
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # Source language check
    if source_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported source language: {source_language}"
        )

    # Target language check
    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported target language: {target_language}"
        )

    # Same language
    if source_language == target_language:
        return text

    source_code = SUPPORTED_LANGUAGES[source_language]
    target_code = SUPPORTED_LANGUAGES[target_language]

    try:
        translator = MyMemoryTranslator(
            source=source_code,
            target=target_code
        )

        translated_text = translator.translate(text)

        if not translated_text:
            raise ValueError("Translation returned an empty result")

        return translated_text

    except Exception as e:
        raise ValueError(
            f"Translation service error: {text} --> {str(e)}"
        )