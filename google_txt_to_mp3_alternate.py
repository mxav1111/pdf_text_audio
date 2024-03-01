import glob
import os
import re

from dotenv import load_dotenv
from google.cloud import texttospeech

load_dotenv()

langcode = os.environ["langcode"]
voicename = os.environ["voicename"]
speakingrate = os.environ["speakingrate"]
file_to_read = os.environ["book"] + ".txt"
file_to_write = os.environ["book"] + "_" + voicename + "_" + speakingrate
removepartial = os.environ["removepartial"]
credential_path = os.environ["credential_path"]
bktnm = os.environ["bktnm"]
location = os.environ["location"]
project_id = os.environ["project_id"]
output_gcs_uri = "gs://" + bktnm + "/" + file_to_write
parent = f"projects/" + project_id + "/locations/" + location
langcode = langcode or "hi-IN"
voicename = voicename or "hi-IN-Neural2-A"
speakingrate = speakingrate or 0.85
pagenumbers = os.environ["pagenumbers"] or "YES"
sentstop = os.environ["sentstop"] or "।"  ## default hindiS LOOK INTO THIS LATER


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


print(f"processing {file_to_read} --> {file_to_write}")
print(f"Using: {langcode} : {voicename} : {speakingrate}")

with open(file_to_read, "r", encoding="utf-8") as f:
    file_in_buffer = f.read()

file_in_buffer = re.sub(r"(?:=!pgB!=.*=!Epg!=\n)+", r"", file_in_buffer)
## word that splits and spans line using hypen is merged
file_in_buffer = re.sub(r"\([^ ]\)-(\n)+", r"\1", file_in_buffer)  
## remove new lines and convert multi spaces to single.
file_in_buffer = re.sub(r"([^ ])-\n", r"\1", file_in_buffer)  
file_in_buffer = re.sub(r"(\n)+", r" ", file_in_buffer)
file_in_buffer = re.sub(r"\n", r" ", file_in_buffer)
## remove new lines and convert multi spaces to single.
file_in_buffer = re.sub(r"[ ][ ]*", r" ", file_in_buffer)  

curr_position_in_utf = 0
utf_buffer_size = len(file_in_buffer.encode("utf-8"))
file_sequence_to_write = 1
start_of_sentence = end_of_sentence = 0
collect_audio_chunk_filenames = "concat:"
while curr_position_in_utf < utf_buffer_size:
    text_chunk = ""
    text_chunk_size = 0
    while text_chunk_size < 2000:
        end_of_sentence = file_in_buffer.find(sentstop, start_of_sentence)
        # sentence couldn't complete or EOF reached, if close to EOF then try to retrieve last pieces.
        if (end_of_sentence == -1):  
            ## get  rest of the all until the END if any half sentences..
            text_chunk = (text_chunk + file_in_buffer[start_of_sentence:])  
            ## time to break outside loop too but in a way that last piece of write can commplete
            curr_position_in_utf = utf_buffer_size  
            break  ## aaaand break out
        # a new quote started
        text_chunk = (text_chunk + file_in_buffer[start_of_sentence : end_of_sentence + 1])  
        start_of_sentence = end_of_sentence + 1
        text_chunk_size = len(text_chunk.encode("utf-8"))
        print(f"start_of_sentence={start_of_sentence},end_of_sentence={end_of_sentence},text_chunk_size={text_chunk_size},len={len(text_chunk)}, curr_position_in_utf={curr_position_in_utf}, utf_buffer_size={utf_buffer_size}")
    print(f'file_in_buffer details:- encodeutflen={len(file_in_buffer.encode("utf-8"))},len={len(file_in_buffer)}, " WHOLEFILE" ')
    print(f"{text_chunk}")
    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
        language_code=langcode,
        name=voicename,
    )
    input = texttospeech.SynthesisInput(text=text_chunk)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=float(speakingrate)
    )
    request = client.synthesize_speech(
        input=input, voice=voice, audio_config=audio_config
    )
    audio_chunk_filename = f"{file_to_write}_{str(file_sequence_to_write).zfill(3)}.mp3"
    text_chunk_filename = f"{file_to_write}_{str(file_sequence_to_write).zfill(3)}.out"

    with open(audio_chunk_filename, "wb") as out:
        out.write(request.audio_content)
    with open(text_chunk_filename, "w", encoding="utf-8") as out:
        out.write(text_chunk)
    print(f"Audio and text content written to file :- {audio_chunk_filename} {text_chunk_filename}")
    collect_audio_chunk_filenames = f"{collect_audio_chunk_filenames}{text_chunk_filename}|"

    curr_position_in_utf += text_chunk_size
    file_sequence_to_write += 1
cmd = f'ffmpeg -y -i "{collect_audio_chunk_filenames}" -c copy {file_to_write}.mp3'

print(f"Merging part files using: {cmd}")
os.system(cmd)
file_to_writeext = file_to_write + ".mp3"
if os.path.isfile(file_to_writeext):
    print(f"{file_to_writeext} successfully created.")
    if removepartial == "YES":
        removeext1 = glob.glob(file_to_write + "*_???.mp3")
        removeext2 = glob.glob(file_to_write + "*_???.out")
        print(f"Removing all part files.. " + str(removeext1) + str(removeext2))
        removefiles1 = map(os.remove, removeext1)
        removefiles2 = map(os.remove, removeext2)
        rmf = list(removefiles1)
        rmf = list(removefiles2)
    else:
        print(f"Partial files not removed because environment variable removepartial is set to {removepartial}")
else:
    print(f"{file_to_writeext} could not be created. You might have partial files {file_to_write}*.out and {file_to_write}*.mp3 available for further diagnosis.")

print(f"\nFinished processing, check {bktnm}: {file_to_write}.mp3")
