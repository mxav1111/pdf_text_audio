import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
load_dotenv()

def list_ms_voices():
# config
 speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
# Create your client
 client = speechsdk.SpeechSynthesizer(speech_config=speech_config)
# Request the list of available voices
 voices_result = client.get_voices_async().get()
 ##print(voices_result.voices)
 print("Voice:")
 for v in voices_result.voices:
    ##print(f"Name:{display_name}|{v.short_name}|{v.locale}|{v.gender}|{v.local_name}|{v.sample_rate}|{v.voice_type}|{v.style_list}")
    print(f"Name:{v.name}|{v.short_name}|{v.locale}|{v.gender}|{v.local_name}|{v.voice_type}|{v.style_list}")

 print()  # Add an empty line for readability

# iterate through the list of voices
 ##print([v.local_name+"\n" for v in voices_result.voices])
## print([v.locale for v in voices_result.voices])


list_ms_voices()

