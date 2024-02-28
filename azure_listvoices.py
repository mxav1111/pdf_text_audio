import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


def list_ms_voices():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )
    client = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    voices_result = client.get_voices_async().get()
    print("Voice:")
    for v in voices_result.voices:
        print(
            f"Name:{v.name}|{v.short_name}|{v.locale}|{v.gender}|{v.local_name}|{v.voice_type}|{v.style_list}"
        )

    print()  # Add an empty line for readability


list_ms_voices()
