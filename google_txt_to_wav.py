import os
import re
from dotenv import load_dotenv
from google.cloud import storage, texttospeech

load_dotenv()


credential_path = os.environ["credential_path"]
project_id = os.environ["project_id"]
location = os.environ["location"]
bktnm = os.environ["bktnm"]

langcode = os.environ["langcode"]
voicename = os.environ["voicename"]
speakingrate = os.environ["speakingrate"]
text_file_to_read = os.environ["book"] + ".txt"
audio_file_to_write = os.environ["book"] + "_" + voicename + "_" + speakingrate + ".wav"

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

def blob_getbytes(bktnm, filename):    ## return the contents of blob as bytes
    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)
    blob = bucket.blob(filename)
    return ( blob.download_as_bytes() )
    
def blob_remove(bktnm, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)
    blob = bucket.blob(filename)
    generation_match_precondition = None  ## set a generation-match precondition to avoid potential race conditions and data corruptions.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation
    blob.delete(if_generation_match=generation_match_precondition)  ## play safe

def txt_to_audio(text_file_to_read, audio_file_to_write):

    with open(text_file_to_read, "r", encoding="utf-8") as f:
        file_in_buffer = f.read()

    file_in_buffer=re.sub(r'(?:=!pgB!=.*=!Epg!=\n)+',r'',file_in_buffer)
    file_in_buffer=re.sub(r'\([^ ]\)-(\n)+',r'\1',file_in_buffer) ## word that splits and spans line using hypen is merged
    file_in_buffer=re.sub(r'([^ ])-\n',r'\1',file_in_buffer) ## remove new lines and convert multi spaces to single.
    file_in_buffer=re.sub(r'(\n)+',r' ',file_in_buffer)
    file_in_buffer=re.sub(r'\n',r' ',file_in_buffer)
    file_in_buffer=re.sub(r'[ ][ ]*',r' ',file_in_buffer)  ## remove new lines and convert multi spaces to single.

    if blob_exists(bktnm, audio_file_to_write):
        print(f"{audio_file_to_write} exists in {bktnm}, removing first..")
        blob_remove(bktnm, audio_file_to_write)
        print(f"{audio_file_to_write} deleted from {bktnm}..")  

    print(f"Creating {audio_file_to_write} in {bktnm}..")

    client       = texttospeech.TextToSpeechLongAudioSynthesizeClient()
    input        = texttospeech.SynthesisInput(text=file_in_buffer)
    audio_config = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=float(speakingrate),)
    voice        = texttospeech.VoiceSelectionParams( language_code=langcode, name=voicename,)
    request      = texttospeech.SynthesizeLongAudioRequest( parent=parent, input=input, audio_config=audio_config, voice=voice, output_gcs_uri=output_gcs_uri,)

    operation    = client.synthesize_long_audio(request=request)
    result       = operation.result(timeout=900)  ## wait upto 15 mins

    print(f"\nFinished processing, check {bktnm}: {audio_file_to_write} as result={result}.", result)
    print(f"\nDownloading {audio_file_to_write}...")

    ## blob_download(bktnm, audio_file_to_write) ## replaced with blob_getbytes using 3 lines below
    audio_contents = blob_getbytes(bktnm, audio_file_to_write)
    with open(audio_file_to_write, "wb") as f:
         f.write(audio_contents)

print(f"processing {text_file_to_read} --> {audio_file_to_write}")
print(f"Using: {langcode} : {voicename} : {speakingrate}")
contents=txt_to_audio(text_file_to_read, audio_file_to_write);
print("done!")
