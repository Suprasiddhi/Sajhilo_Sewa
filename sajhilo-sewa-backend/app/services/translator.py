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
        if not text:
            return ""
        
        text_lower = text.lower().strip()
        
        # 1. Quick Dictionary Check
        if text_lower in self.mapping:
            return self.mapping[text_lower]
        
        # 2. API Call (if available)
        if _use_api:
            try:
                # googletrans is synchronous, but we can wrap it if needed. 
                # For single words, it's fast enough (~200ms).
                result = self.translator.translate(text, dest='ne')
                # Cache the result for future use
                self.mapping[text_lower] = result.text
                return result.text
            except Exception as e:
                print(f"⚠️ Translation API Error: {e}")
                return text  # Return original as fallback
        
        return text

# Global singleton
translator_service = TranslatorService()
