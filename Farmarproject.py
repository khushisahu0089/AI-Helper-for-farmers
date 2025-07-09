import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from PIL import Image

import json

json_file_path = r"C:\\Users\\Karishma\\OneDrive\\Desktop\\AI Farmar Project\\plant_disease_advice.json"

with open(json_file_path, "r", encoding='utf-8') as file:
    disease_advice = json.load(file)

print(disease_advice)

def fake_image_analysis():
    return "brown spots"

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info(" Listening... Please speak about your plant issue.")
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_data, language='hi-IN')
            st.success(f" {text}")
            return text
        except sr.UnknownValueError:
            st.error(" Sorry, could not understand the audio.")
        except sr.RequestError:
            st.error(" Request failed. Check your internet connection.")

def translate_to_english(text):
    translator = Translator()
    detected = translator.detect(text).lang
    if detected == 'hi':
        translated = translator.translate(text, src='hi', dest='en').text
        st.info(f"अनुवाद (Hindi ➜ English): {translated}")
        return translated
    return text

def translate_to_hindi(text):
    translator = Translator()
    translated = translator.translate(text, src='en', dest='hi').text
    return translated

def speak_text(text, lang_code='hi'):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("advice.mp3")
    audio_file = open("advice.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")

def match_symptom(text):
    text = text.lower()
    for symptom, advice in disease_advice.items():
        if symptom in text:
            advice_hi = translate_to_hindi(advice)
            st.markdown(f""" **Detected Symptom**: {symptom}  
**Advice (English)**: {advice}  
 **सलाह (Hindi)**: {advice_hi}""")

            speak_text(advice_hi, lang_code='hi')
            return
    st.warning(" Sorry, I couldn't identify any known symptoms.")

st.title(" AI Helper for Farmers (किसानों के लिए एआई सहायक)")

st.header(" Upload Plant Image")
image = st.file_uploader("Upload a photo of the plant leaf", type=["jpg", "jpeg", "png"])
if image:
    st.image(image, caption="Uploaded Leaf Image", use_container_width=True)

    symptom_from_image = fake_image_analysis()
    st.success(f" Detected from Image: {symptom_from_image}")
    match_symptom(symptom_from_image)

st.header(" बोलकर समस्या बताएं (Voice Input)")
if st.button(" Start Voice Recording"):
    voice_text = transcribe_audio()
    if voice_text:
        translated_voice = translate_to_english(voice_text)
        match_symptom(translated_voice)

st.header(" टाइप करके समस्या बताएं (Typing Input)")
typed_text = st.text_input(" समस्या यहां लिखें (हिंदी या अंग्रेज़ी में)")
if st.button(" Submit"):
    if typed_text.strip() != "":
        translated_text = translate_to_english(typed_text)
        match_symptom(translated_text)
    else:
        st.warning("कृपया कुछ लिखें।")


weather_to_crop_advice = {
    "गर्मी": ["मक्का", "कपास", "गन्ना", "अरहर", "मूंग"],
    "सर्दी": ["गेहूं", "सरसों", "चना", "मटर", "जौ"],
    "बरसात": ["धान", "सोयाबीन", "मक्का", "मूंगफली", "उड़द"],
    "summer": ["Maize", "Cotton", "Sugarcane", "Pigeon pea", "Green gram"],
    "winter": ["Wheat", "Mustard", "Chickpea", "Peas", "Barley"],
    "monsoon": ["Rice", "Soybean", "Maize", "Groundnut", "Black gram"]
}

def get_crop_advice(season):
    translator = Translator()
    season = season.lower().strip()

    if season in weather_to_crop_advice:
        crops = weather_to_crop_advice[season]
        crops_list_en = ", ".join(crops)

        if all(ord(c) < 128 for c in crops[0]):  
            crops_hi = [translator.translate(crop, src='en', dest='hi').text for crop in crops]
        else:  
            crops_hi = crops

        crops_hi_str = ", ".join(crops_hi)

        hindi_title = {
            "summer": "गर्मी",
            "winter": "सर्दी",
            "monsoon": "बरसात"
        }.get(season, season)

        st.markdown(f""" मौसम: *{hindi_title}*  
                     **Recommended Crops (English)**: {crops_list_en}  
                     **अनुशंसित फसलें (Hindi)**: {crops_hi_str}""")

        tts_text = f"{hindi_title} के मौसम में आप {crops_hi_str} की खेती कर सकते हैं।"
        speak_text(tts_text, lang_code='hi')
    else:
        st.warning(" कृपया सही मौसम दर्ज करें (जैसे: गर्मी, सर्दी, बरसात या summer, winter, monsoon)।")
        speak_text("कृपया सही मौसम का नाम दर्ज करें।", lang_code='hi')

st.header(" मौसम के अनुसार फसल सुझाव (Crop Advice by Season)")
season_input = st.text_input(" मौसम बताएं (उदाहरण: गर्मी, सर्दी, बरसात या summer, winter, monsoon):")
if st.button(" फसल सुझाव दें"):
    if season_input.strip() != "":
        get_crop_advice(season_input)
    else:
        st.warning("⚠ कृपया मौसम दर्ज करें।")
        speak_text("कृपया मौसम दर्ज करें।", lang_code='hi')
