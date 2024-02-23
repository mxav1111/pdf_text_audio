"""Synthesizes speech from the input string of text or ssml.
Make sure to be working in a virtual environment.
Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
"""
f = open('myfile.txt')
contents = f.read()
print(contents)
177657:69257:
"""

import os
import sys
import re
import glob
import tempfile
import multiprocessing
from   google.cloud import storage
from   google.cloud import texttospeech
## from   ffmpeg import FFmpeg, Progress, FFmpegFileNotFound, FFmpegInvalidCommand

 
langcode=os.environ['langcode'] ; voicename=os.environ['voicename']        ; speakingrate=os.environ['speakingrate'] 
ftr=os.environ['book']+".txt" ; ftw=os.environ['book']+"_"+voicename+"_"+speakingrate; removepartial=os.environ['removepartial']
ftw1=ftr+".out"
credential_path = os.environ['credential_path']; bktnm=os.environ['bktnm']
location = os.environ['location'] ; project_id = os.environ['project_id'] ; output_gcs_uri = "gs://"+bktnm+"/"+ftw
parent = f"projects/"+project_id+"/locations/"+location
langcode = langcode or "hi-IN"  ; voicename=voicename or "hi-IN-Neural2-A" ; speakingrate=speakingrate or 0.85
pagenumbers=os.environ['pagenumbers'] or "YES"
sentstop=os.environ["sentstop"] or u"।"  ## default hindiS LOOK INTO THIS LATER
## sentstop=u"।"  ## default hindiS LOOK INTO THIS LATER
## sentstop=str(sentstop, encoding='utf-8')
## bytes_object = bytes(sentstop, 'utf-8')
## sentstop = bytes_object.decode('utf-8')


print ('processing ' + ftr +' --> ' + ftw + "\nUsing: "+ langcode+" : "+voicename+" : "+str(speakingrate))
f= open(ftr,"r",encoding="utf-8"); fc= f.read();  
fc=re.sub(r'(?:=!pgB!=.*=!Epg!=\n)+',r'',fc)
fc=re.sub(r'\([^ ]\)-(\n)+',r'\1',fc) ## word that splits and spans line using hypen is merged
fc=re.sub(r'([^ ])-\n',r'\1',fc) ## remove new lines and convert multi spaces to single.
fc=re.sub(r'(\n)+',r' ',fc); fc=re.sub(r'\n',r' ',fc); fc=re.sub(r'[ ][ ]*',r' ',fc)  ## remove new lines and convert multi spaces to single.
strtpnt=0
currulen=0; ufsz=len(fc.encode('utf-8'))
flnum=1
# str0=fc
ssen=esen=0
finalout="concat:"
while currulen < ufsz:
 str1=""
 str1ulen=0
 #print(f'pos={pos},encodeutflen={len(str1.encode('utf-8'))},len={len(str1)}, string={str1}');
 while str1ulen < 2000:
  # esen=str0.find(sentstop,ssen)
  esen=fc.find(sentstop,ssen)
  if esen==-1: # sentence couldn't complete or EOF reached, if close to EOF then try to retrieve last pieces.
   str1=str1+fc[ssen:] ## get  rest of the all until the END if any half sentences..
   currulen=ufsz ## time to break outside loop too but in a way that last piece of write can commplete
   break ## aaaand break out
  str1=str1+fc[ssen:esen+1] # a new quote started
  ssen=esen+1
  str1ulen=len(str1.encode('utf-8'))
  print(f'ssen={ssen},esen={esen},str1ulen={str1ulen},len={len(str1)}, currulen={currulen}, ufsz={ufsz}');
 print(f'fc details:- encodeutflen={len(fc.encode("utf-8"))},len={len(fc)}, " WHOLEFILE" ');
 print(f'{str1}');
 client           = texttospeech.TextToSpeechClient()
 voice            = texttospeech.VoiceSelectionParams( language_code=langcode, name=voicename,)
 input            = texttospeech.SynthesisInput( text=str1 )
 audio_config     = texttospeech.AudioConfig( audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=float(speakingrate) )
 request          = client.synthesize_speech( input=input, voice=voice, audio_config=audio_config)
 of1= ftw +"_"+str(flnum).zfill(3)+".mp3" 
 of2= ftw +"_"+str(flnum).zfill(3)+".out"
 #with tempfile.TemporaryFile() as tmp1:
 # tmp1.write(request.audio_content)
  
 with open(of1,  "wb")  as out:
  out.write(request.audio_content)
 with open(of2, "w", encoding="utf-8")  as out:
  out.write(str1)
 print(f'Audio and text content written to file :- {of1} {of2}')
 ##finalout=finalout+" -i "+of1
 finalout=finalout+of1+"|"
 currulen+=str1ulen; flnum+=1
cmd='ffmpeg -y -i '+'"'+finalout+'"'+' -c copy '+ftw+".mp3"

print(f"Merging part files using: {cmd}"); os.system(cmd)
ftwext=ftw+".mp3"
if os.path.isfile(ftwext):
 print (f"{ftwext} successfully created.");
 if removepartial=="YES":
  removeext1 = glob.glob(ftw+"*_???.mp3");  removeext2 = glob.glob(ftw+"*_???.out")
  print( f"Removing all part files.. "+str(removeext1 ) + str(removeext2) )
  removefiles1=map(os.remove, removeext1 ); removefiles2=map(os.remove, removeext2) 
  rmf=list(removefiles1); rmf=list(removefiles2);
 else:
  print( f"Partial files not removed because environment variable removepartial is set to {removepartial}" )
else:
 print (f"{ftwext} could not be created. You might have partial files {ftw}*.out and {ftw}*.mp3 available for further diagnosis.");
  
print( f"\nFinished processing, check {bktnm}: {ftw}.mp3" )

