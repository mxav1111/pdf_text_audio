import os
from   dotenv import load_dotenv
from   google.cloud import storage
from   google.cloud import texttospeech
#### import sys

load_dotenv()

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
# ftr=sys.argv[1]+".txt"; ftw=sys.argv[1]+".wav" ;  exit()
#credential_path = "C:/final_pre/gogtts/crypto-canyon-407901-1daf7a7aa44c.json";  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
langcode=os.environ['langcode'] ; voicename=os.environ['voicename']        ; speakingrate=os.environ['speakingrate'] 
ftr=os.environ['book']+".txt" ; ftw=os.environ['book']+"_"+voicename+"_"+speakingrate+".wav"
credential_path = os.environ['credential_path']; bktnm=os.environ['bktnm']
location = os.environ['location'] ; project_id = os.environ['project_id'] ; output_gcs_uri = "gs://"+bktnm+"/"+ftw
parent = f"projects/"+project_id+"/locations/"+location
langcode = langcode or "hi-IN"  ; voicename=voicename or "hi-IN-Neural2-A" ; speakingrate=speakingrate or 0.85
print ('processing ' + ftr +' --> ' + ftw + "\nUsing: "+ langcode+" : "+voicename+" : "+str(speakingrate))
## list_voices()
f=open(ftr,"r",encoding="utf-8"); fc=f.read(); f=open(ftw,"w",encoding="utf-8")

##with open(ftw, "wb") as out:
## out.write(fc) # Write the response to the output file.

"""
Synthesizes long input, writing the resulting audio to `output_gcs_uri`.
Example usage: synthesize_long_audio('12345', 'us-central1', 'gs://{BUCKET_NAME}/{OUTPUT_FILE_NAME}.wav')
"""


## print (output_gcs_uri+" "+parent)
if blob_exists(bktnm,ftw): print(f'{ftw} exists in {bktnm}, removing..');  blob_remove(bktnm,ftw); print(f'{ftw} deleted from {bktnm}..') ##  = storage_client.list_blobs(bucket)
print(f'Creating {ftw} in {bktnm}..')    
client = texttospeech.TextToSpeechLongAudioSynthesizeClient(); input = texttospeech.SynthesisInput( text=fc )

# Select the type of audio file you want returned
## audio_config = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.MP3
### audio_config = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.LINEAR16 )
audio_config = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.LINEAR16, speaking_rate=float(speakingrate) )

##voice = texttospeech.VoiceSelectionParams( language_code="en-US",  name="en-US-Standard-A", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE )
##voice = texttospeech.VoiceSelectionParams( language_code="hi-IN",  name="hi-IN-Wavenet-D",  ssml_gender=texttospeech.SsmlVoiceGender.FEMALE )
voice   = texttospeech.VoiceSelectionParams( language_code=langcode, name=voicename,)

## response = client.synthesize_speech( input=synthesis_input, voice=voice, audio_config=audio_config )
### request = texttospeech.SynthesizeLongAudioRequest( parent=parent, input=input, audio_config=audio_config, voice=voice, output_gcs_uri=output_gcs_uri, )
request = texttospeech.SynthesizeLongAudioRequest( parent=parent, input=input, audio_config=audio_config, voice=voice, output_gcs_uri=output_gcs_uri)

operation = client.synthesize_long_audio(request=request)
# Set a deadline for your LRO to finish. 300 seconds is reasonable, but can be adjusted depending on the length of the input.
# If the operation times out, that likely means there was an error. In that case, inspect the error, and try again.
result = operation.result(timeout=900) ## wait upto 15 mins
##print( "\nFinished processing, check your GCS bucket to find your audio file! Printing what should be an empty result: ", result, )
print( f"\nFinished processing, check {bktnm}: {ftw} as result={result}.", result, )
print( f"\nDownloading {ftw}..." ); blob_download(bktnm, ftw); print( "done!")

# Perform the text-to-speech request on the text input with the selected
# voice parameters and audio file type

# The response's audio_content is binary.
## with open(ftw, "wb") as out:
    # Write the response to the output file.
##     out.write(response.audio_content)
  #  print('Audio content written to file "output.mp3"')


