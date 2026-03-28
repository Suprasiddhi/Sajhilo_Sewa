export const gestureToNepali = {
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
};

export const translateGesture = (english) => {
  return gestureToNepali[english.toLowerCase()] || english;
};
