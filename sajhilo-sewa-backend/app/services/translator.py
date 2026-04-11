import os
import json
from concurrent.futures import ThreadPoolExecutor

# Use 'deep_translator' for a more stable free translation engine
try:
    from deep_translator import GoogleTranslator
    _use_api = True
except ImportError:
    _use_api = False
    print("⚠️ deep-translator not installed. Install with 'pip install deep-translator'")

class TranslatorService:
    def __init__(self):
        # We don't instantiate the translator globally if it's stateless, 
        # but deep_translator allows us to prepare a translator instance.
        self.translator = GoogleTranslator(source='auto', target='ne') if _use_api else None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Local fallback dictionary for instant response on common gestures
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
        Translates text from English to Nepali.
        Logic:
        1. Local dictionary check (instant)
        2. Deep Translator API check (network)
        3. Fallback to original text
        """
        if text is None or not str(text).strip():
            return ""
        
        text_str = str(text).lower().strip()
        
        # 1. Quick Dictionary Check
        if text_str in self.mapping:
            translated = self.mapping[text_str]
            print(f"✅ Local Dictionary Translation: '{text}' -> '{translated}'")
            return translated
        
        # 2. Deep-Translator API Call
        if _use_api and self.translator:
            try:
                # deep-translator's translate() is straightforward
                translated = self.translator.translate(text)
                if translated:
                    # Cache the result locally for this session
                    self.mapping[text_str] = translated
                    return translated
            except Exception as e:
                # Catch connection errors or API issues
                print(f"⚠️ Translation Service Error: {e}")
                return text  # Return original as fallback
        
        return text

# Global singleton
translator_service = TranslatorService()
