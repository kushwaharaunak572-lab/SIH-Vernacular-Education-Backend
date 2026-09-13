from deep_translator import MyMemoryTranslator, GoogleTranslator


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

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


# ============================================================
# GOOGLE TRANSLATOR LANGUAGE CODES
# ============================================================

GOOGLE_LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Odia": "or",
    "Assamese": "as",
    "Nepali": "ne",
    "Urdu": "ur",
}


# ============================================================
# LANGUAGE ALIASES
# ============================================================

LANGUAGE_ALIASES = {

    # English
    "english": "English",
    "en": "English",
    "en-in": "English",
    "en-gb": "English",

    # Hindi
    "hindi": "Hindi",
    "hi": "Hindi",
    "hi-in": "Hindi",

    # Bengali
    "bengali": "Bengali",
    "bn": "Bengali",
    "bn-in": "Bengali",

    # Gujarati
    "gujarati": "Gujarati",
    "gu": "Gujarati",
    "gu-in": "Gujarati",

    # Marathi
    "marathi": "Marathi",
    "mr": "Marathi",
    "mr-in": "Marathi",

    # Punjabi
    "punjabi": "Punjabi",
    "pa": "Punjabi",
    "pa-in": "Punjabi",

    # Tamil
    "tamil": "Tamil",
    "ta": "Tamil",
    "ta-in": "Tamil",

    # Telugu
    "telugu": "Telugu",
    "te": "Telugu",
    "te-in": "Telugu",

    # Kannada
    "kannada": "Kannada",
    "kn": "Kannada",
    "kn-in": "Kannada",

    # Malayalam
    "malayalam": "Malayalam",
    "ml": "Malayalam",
    "ml-in": "Malayalam",

    # Odia
    "odia": "Odia",
    "or": "Odia",
    "or-in": "Odia",

    # Assamese
    "assamese": "Assamese",
    "as": "Assamese",
    "as-in": "Assamese",

    # Nepali
    "nepali": "Nepali",
    "ne": "Nepali",
    "ne-np": "Nepali",

    # Urdu
    "urdu": "Urdu",
    "ur": "Urdu",
    "ur-in": "Urdu",
    "ur-pk": "Urdu",
}


# ============================================================
# NORMALIZE LANGUAGE
# ============================================================

def normalize_language(language: str) -> str:

    if not language:
        raise ValueError(
            "Language cannot be empty"
        )

    language_key = language.strip().lower()

    # Direct language name
    for language_name in SUPPORTED_LANGUAGES:

        if language_key == language_name.lower():
            return language_name

    # Language code / alias
    if language_key in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[language_key]

    raise ValueError(
        f"Unsupported language: {language}"
    )


# ============================================================
# TRANSLATE USING MYMEMORY
# ============================================================

def translate_with_mymemory(
    text: str,
    source_language: str,
    target_language: str
) -> str:

    source_code = SUPPORTED_LANGUAGES[
        source_language
    ]

    target_code = SUPPORTED_LANGUAGES[
        target_language
    ]

    translator = MyMemoryTranslator(
        source=source_code,
        target=target_code
    )

    translated_text = translator.translate(text)

    if not translated_text:
        raise ValueError(
            "MyMemory returned an empty result"
        )

    return translated_text


# ============================================================
# TRANSLATE USING GOOGLE
# ============================================================

def translate_with_google(
    text: str,
    source_language: str,
    target_language: str
) -> str:

    source_code = GOOGLE_LANGUAGE_CODES[
        source_language
    ]

    target_code = GOOGLE_LANGUAGE_CODES[
        target_language
    ]

    translator = GoogleTranslator(
        source=source_code,
        target=target_code
    )

    translated_text = translator.translate(text)

    if not translated_text:
        raise ValueError(
            "Google Translator returned an empty result"
        )

    return translated_text


# ============================================================
# MAIN TRANSLATION FUNCTION
# ============================================================

def translate_text(
    text: str,
    source_language: str,
    target_language: str
) -> str:

    # --------------------------------------------------------
    # Empty text check
    # --------------------------------------------------------

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty"
        )

    # --------------------------------------------------------
    # Normalize languages
    # --------------------------------------------------------

    source_language_name = normalize_language(
        source_language
    )

    target_language_name = normalize_language(
        target_language
    )

    # --------------------------------------------------------
    # Same language
    # --------------------------------------------------------

    if source_language_name == target_language_name:
        return text

    # --------------------------------------------------------
    # First try MyMemory
    # --------------------------------------------------------

    try:

        return translate_with_mymemory(
            text=text,
            source_language=source_language_name,
            target_language=target_language_name
        )

    except Exception as mymemory_error:

        print(
            "MyMemory translation failed."
        )

        print(
            f"Reason: {mymemory_error}"
        )

    # --------------------------------------------------------
    # If MyMemory fails, use Google Translator
    # --------------------------------------------------------

    try:

        return translate_with_google(
            text=text,
            source_language=source_language_name,
            target_language=target_language_name
        )

    except Exception as google_error:

        print(
            "Google translation also failed."
        )

        print(
            f"Reason: {google_error}"
        )

        raise ValueError(
            "Translation service is temporarily unavailable. "
            "Please try again later."
        )