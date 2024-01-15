"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.
Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""

import os
import sys
import re
from google.cloud import storage
from google.cloud import texttospeech

def blob_exists(bktnm, filename):
    storage_client = storage.Client(); bucket = storage_client.bucket(bktnm); 
    blob = bucket.blob(filename)
    return blob.exists()
def blob_download(bktnm, filename):
    storage_client = storage.Client(); bucket = storage_client.bucket(bktnm); 
    blob = bucket.blob(filename)
    blob.download_to_filename(filename)
def blob_remove(bktnm, filename):
    storage_client = storage.Client(); bucket = storage_client.bucket(bktnm); 
    blob = bucket.blob(filename)
    generation_match_precondition = None  ## set a generation-match precondition to avoid potential race conditions and data corruptions. 
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation
    blob.delete(if_generation_match=generation_match_precondition)  ## play safe

langcode=os.environ['langcode'] ; voicename=os.environ['voicename']        ; speakingrate=os.environ['speakingrate'] 
ftr=os.environ['book']+".txt" ; ftw=os.environ['book']+"_"+voicename+"_"+speakingrate+".wav"
ftw1=ftr+".out"
credential_path = os.environ['credential_path']; bktnm=os.environ['bktnm']
location = os.environ['location'] ; project_id = os.environ['project_id'] ; output_gcs_uri = "gs://"+bktnm+"/"+ftw
parent = f"projects/"+project_id+"/locations/"+location
langcode = langcode or "hi-IN"  ; voicename=voicename or "hi-IN-Neural2-A" ; speakingrate=speakingrate or 0.85
print ('processing ' + ftr +' --> ' + ftw + "\nUsing: "+ langcode+" : "+voicename+" : "+str(speakingrate))
## list_voices()
f=open(ftr,"r",encoding="utf-8"); fc=f.read();  
fc=re.sub(r'(?:=!pgB!=.*=!Epg!=\n)+',r'',fc)
fc=re.sub(r'(\n)+',r' ',fc); fc=re.sub(r'\n',r' ',fc); fc=re.sub(r'[ ][ ]*',r' ',fc)  ## remove new lines and convert multi spaces to single.
#print (fc) ;
#exit();
f=open(ftw,"w",encoding="utf-8")
with open(ftw1, "w", encoding="utf-8") as f:
     f.write(fc)
"""
Synthesizes long input, writing the resulting audio to `output_gcs_uri`.
Example usage: synthesize_long_audio('12345', 'us-central1', 'gs://{BUCKET_NAME}/{OUTPUT_FILE_NAME}.wav')
"""
if blob_exists(bktnm,ftw): print(f'{ftw} exists in {bktnm}, removing..');  blob_remove(bktnm,ftw); print(f'{ftw} deleted from {bktnm}..') ##  = storage_client.list_blobs(bucket)
print(f'Creating {ftw} in {bktnm}..')    
client           = texttospeech.TextToSpeechLongAudioSynthesizeClient();
voice            = texttospeech.VoiceSelectionParams( language_code=langcode, name=voicename,)
audio_config     = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=float(speakingrate) )
input            = texttospeech.SynthesisInput( text=fc )
request          = texttospeech.SynthesizeLongAudioRequest( parent=parent, input=input, audio_config=audio_config, voice=voice, output_gcs_uri=output_gcs_uri)
operation        = client.synthesize_long_audio(request=request)
result           = operation.result(timeout=900) ## wait upto 15 mins
print( f"\nFinished processing, check {bktnm}: {ftw} as result={result}.", result, )
print( f"\nDownloading {ftw}..." ); blob_download(bktnm, ftw); print( "done!")

