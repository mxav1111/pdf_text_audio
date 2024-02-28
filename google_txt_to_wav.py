import os

from dotenv import load_dotenv
from google.cloud import storage, texttospeech

load_dotenv()


langcode = os.environ["langcode"]
voicename = os.environ["voicename"]
speakingrate = os.environ["speakingrate"]
text_file_to_read = os.environ["book"] + ".txt"
audio_file_to_write = os.environ["book"] + "_" + voicename + "_" + speakingrate + ".wav"
credential_path = os.environ["credential_path"]
bktnm = os.environ["bktnm"]
location = os.environ["location"]
project_id = os.environ["project_id"]
output_gcs_uri = "gs://" + bktnm + "/" + audio_file_to_write
parent = f"projects/" + project_id + "/locations/" + location
langcode = langcode or "hi-IN"
voicename = voicename or "hi-IN-Neural2-A"
speakingrate = speakingrate or 0.85


def blob_exists(bktnm, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)
    blob = bucket.blob(filename)
    return blob.exists()


def blob_download(bktnm, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)
    blob = bucket.blob(filename)
    blob.download_to_filename(filename)


def blob_remove(bktnm, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)
    blob = bucket.blob(filename)
    generation_match_precondition = None  ## set a generation-match precondition to avoid potential race conditions and data corruptions.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation
    blob.delete(if_generation_match=generation_match_precondition)  ## play safe


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


print(f"processing {text_file_to_read} --> {audio_file_to_write}")
print(f"Using: {langcode} : {voicename} : {speakingrate}")

with open(text_file_to_read, "r", encoding="utf-8") as f:
    fc = f.read()

f = open(audio_file_to_write, "w", encoding="utf-8")

if blob_exists(bktnm, audio_file_to_write):
    print(f"{audio_file_to_write} exists in {bktnm}, removing first..")
    blob_remove(bktnm, audio_file_to_write)
    print(f"{audio_file_to_write} deleted from {bktnm}..")  

print(f"Creating {audio_file_to_write} in {bktnm}..")

client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
input = texttospeech.SynthesisInput(text=fc)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=float(speakingrate),
)
voice = texttospeech.VoiceSelectionParams(
    language_code=langcode,
    name=voicename,
)
request = texttospeech.SynthesizeLongAudioRequest(
    parent=parent,
    input=input,
    audio_config=audio_config,
    voice=voice,
    output_gcs_uri=output_gcs_uri,
)

operation = client.synthesize_long_audio(request=request)
result = operation.result(timeout=900)  ## wait upto 15 mins
print(f"\nFinished processing, check {bktnm}: {audio_file_to_write} as result={result}.", result)
print(f"\nDownloading {audio_file_to_write}...")
blob_download(bktnm, audio_file_to_write)
print("done!")
