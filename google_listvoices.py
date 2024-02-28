from dotenv import load_dotenv
from google.cloud import texttospeech

load_dotenv()


def list_voices():

    client = texttospeech.TextToSpeechClient()

    voices = client.list_voices()

    for voice in voices.voices:
        print(f"Name: {voice.name}")

        for language_code in voice.language_codes:
            print(f"Supported language: {language_code}")

        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

        print(f"SSML Voice Gender: {ssml_gender.name}")
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")


list_voices()
