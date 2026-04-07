import os
import json
from concurrent.futures import ThreadPoolExecutor

# You can use 'googletrans' for a free wrapper, or 'google-cloud-translate' for the official API.
# For this implementation, we will use 'googletrans' (free) with a local dictionary fallback.
try:
    from googletrans import Translator as GoogleTranslator
    _use_api = True
except ImportError:
    _use_api = False
    print("⚠️ googletrans not installed. Install with 'pip install googletrans==4.0.0-rc1'")

class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator() if _use_api else None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Local fallback dictionary (merged from frontend src/utils/translation.js)
        self.mapping = {
            "bathroom": "शौचालय",
            "bill": "बिल",
            "bottle": "बोतल",
            "clean": "सफा",
            "coffee": "कफी",
            "cold": "चिसो",
            "food": "खाना",
            "hello": "नमस्ते",
            "hot": "तातो",
            "no": "होइन",
            "order": "অর্ডার",
            "please": "कृपया",
            "tea": "चिया",
            "thank you": "धन्यवाद",
            "wait": "पर्खनुहोस्",
            "want": "चाहन्छु",
            "water": "पानी",
            "yes": "हो"
        }

    def translate(self, text: str) -> str:
        """
        Translates text to Nepali. 
        Checks local dictionary first for speed, then calls API.
        """
        if text is None or not str(text).strip():
            return ""
        
        text_str = str(text).lower().strip()
        
        # 1. Quick Dictionary Check
        if text_str in self.mapping:
            return self.mapping[text_str]
        
        # 2. API Call (if available)
        if _use_api and self.translator:
            try:
                result = self.translator.translate(text, dest='ne')
                if result and hasattr(result, 'text') and result.text:
                    translated = str(result.text)
                    # Cache the result for future use
                    self.mapping[text_str] = translated
                    return translated
            except Exception as e:
                # This catches the common "NoneType found" error in googletrans
                if "NoneType" not in str(e):
                    print(f"⚠️ Translation API Error: {e}")
                return text  # Return original as fallback
        
        return text

# Global singleton
translator_service = TranslatorService()
