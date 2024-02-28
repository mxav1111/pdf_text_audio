import os

from dotenv import load_dotenv

load_dotenv()

background_audio_filename = os.environ["bga"]
voicename = os.environ["voicename"]
speakingrate = os.environ["speakingrate"]
langcode = os.environ["langcode"]

if langcode == "NULL":
    langcode = ""
    voicename = ""
    speakingrate = ""
    sep = ""
else:
    voicename = os.environ["voicename"]
    speakingrate = os.environ["speakingrate"]
    sep = "_"

audio_filename = os.environ["book"] + sep + voicename + sep + speakingrate
removepartial = os.environ["removepartial"]
credential_path = os.environ["credential_path"]
bktnm = os.environ["bktnm"]
location = os.environ["location"]
project_id = os.environ["project_id"]

output_gcs_uri = "gs://" + bktnm + "/" + audio_filename
parent = f"projects/" + project_id + "/locations/" + location
langcode = langcode or "hi-IN"
voicename = voicename or "hi-IN-Neural2-A"
speakingrate = speakingrate or 0.85
pagenumbers = os.environ["pagenumbers"] or "YES"


print(f"processing {audio_filename}")
print(f"Using: {langcode} : {voicename} : {speakingrate}")

voice_audio_filename = audio_filename + ".mp3"
if not os.path.isfile(voice_audio_filename):
    voice_audio_filename = audio_filename + ".wav"
audio_filenameext = audio_filename + "_m.mp3"

exec_os_command = f'ffmpeg -hide_banner -y -i {voice_audio_filename} -stream_loop -1 -i {background_audio_filename} -lavfi "[1:a]volume=0.1,apad[A];[0:a][A]amerge[out]" -map [out]:a -shortest -b:a 192k {audio_filenameext}'

print(f"Merging {voice_audio_filename} and {background_audio_filename} : {audio_filenameext}")
print(f"using: {exec_os_command}")

os.system(exec_os_command)
if os.path.isfile(audio_filenameext):
    print(f"{audio_filenameext} successfully created.")
else:
    print(f"{audio_filenameext} could not be created.")

print(f"\nFinished processing, check : {audio_filenameext}")
