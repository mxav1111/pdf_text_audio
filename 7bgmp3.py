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

 
bga=os.environ['bga'] ; voicename=os.environ['voicename']        ; speakingrate=os.environ['speakingrate'] 
langcode=os.environ['langcode']
if (langcode=="NULL"):
 langcode="";voicename="";speakingrate="";sep="";
else:
 voicename=os.environ['voicename'] ; speakingrate=os.environ['speakingrate'] ;sep="_"

ftr=os.environ['book']+".txt" ; ftw=os.environ['book']+sep+voicename+sep+speakingrate; removepartial=os.environ['removepartial']
ftw1=ftr+".out"
credential_path = os.environ['credential_path']; bktnm=os.environ['bktnm']
location = os.environ['location'] ; project_id = os.environ['project_id'] ; output_gcs_uri = "gs://"+bktnm+"/"+ftw
parent = f"projects/"+project_id+"/locations/"+location
langcode = langcode or "hi-IN"  ; voicename=voicename or "hi-IN-Neural2-A" ; speakingrate=speakingrate or 0.85
pagenumbers=os.environ['pagenumbers'] or "YES"
sentstop=os.environ["sentstop"] or u"।"  ## default hindiS LOOK INTO THIS LATER
sentstop=u"।"  ## default hindiS LOOK INTO THIS LATER

## sentstop=str(sentstop, encoding='utf-8')
## bytes_object = bytes(sentstop, 'utf-8')
## sentstop = bytes_object.decode('utf-8')


print ('processing ' + ftr +' --> ' + ftw + "\nUsing: "+ langcode+" : "+voicename+" : "+str(speakingrate))
flnum=1
# str0=fc
ssen=esen=0
fga=ftw+'.mp3'
if not os.path.isfile(fga):
 fga=ftw+'.wav'
ftwext=ftw+'_m.mp3'
 
cmd='ffmpeg -hide_banner -y -i '+fga+' -stream_loop -1 -i '+bga+' -lavfi "[1:a]volume=0.1,apad[A];[0:a][A]amerge[out]" -map [out]:a -shortest -b:a 192k '+ftwext
print(f"Merging {fga} and {bga} : {ftwext} \n using: {cmd}"); 
os.system(cmd)
if os.path.isfile(ftwext):
 print (f"{ftwext} successfully created.");
else:
 print (f"{ftwext} could not be created.");
  
print( f"\nFinished processing, check : {ftwext}" )

