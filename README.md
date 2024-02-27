These are set of scripts that will help to convert scanned pdf (such as old books) to UTF-8 based text files. Once you finish editing text files with appropriate corrections, it will also help to create audio file either MP3 or .WAV (linear16). This project is made and tested on windows as well as linux (debian). Please see environment .cmd file or .sh file for linux and read on...

While this is tested with English and Hindi/Sanskrit texts; it is expected to work on other UTF-8 based files too as long as it is supported by google cloud vision and TextToSpeech libraries or Microsoft.

PROJECT IS  TESTED WITH UNIX/LINUX environments as well. Instead of .cmd file, use . ./myenv.linux.sh can be used after editing appropriate environment variable pointers.

While looking for converting scanned pdfs to audio, could not find good complete solution. This project uses Google (or Microsoft) provided neural voices and it is flexible to allow for language and voice selection as google continues to releases new voices with ongoing improvements in AI.

PREREQS: 

Tested with python 3.9 (linux) or 3.12 (windows).
1. pip install -r requirements.txt
   
3. apt-get install ffmpeg (or install from https://gyan.dev for windows)
   
5. Must have google cloud account (or MS azure account) with storage bucket, project id, location and application credentials json file and similarly Microsoft's cognitive and documentintelligence keys.
   
7. update the .env accordingly as follows  :-
   
4A) Environment should be set as below. Example cmd or shell script is provided. Just update and run the same. book_file_name below should be without extension and avoid spaces in filename (rename otherwise). For example, if Book File Name is BE_HAPPY.PDF then set book=BE_HAPPY scripts will automatically create BE_HAPPY.txt , BE_HAPPY.wav , BE_HAPPY.mp3 , BE_HAPPY.json etc using BE_HAPPY.PDF. Actual Source file MUST have .PDF extension. 


Sample .env file is provided. Here's some explanation.
======================================================
book=pdf_book_file_name_without_extension 

GOOGLE_APPLICATION_CREDENTIALS=C:/final_pre/gogtts/gcreds.json 

credential_path=%GOOGLE_APPLICATION_CREDENTIALS% 

project_id=gprojid 

location=us-west1 

bktnm=bucketname 

langcode=en-IN 

voicename=en-IN-Neural2-C 

speakingrate=0.85 

REM Pagenumbers are inserted into text file to help compare with .pdf during verification and corrections in text file for manual post scan compariosn. 

set pagenumbers=YES 

set sentstop=� 

set removepartial=YES

set bga=background_music.mp3


4A) sentstop variable is sentence stop character. It can be different in different languages. It has been tested with hindi and english language. It is used in buffered mp3 creation. (when TextToSpeechLongAudioSynthesizeClient api fails)

removepartial variable helps diagnose if mp3 generator fails to merge partial mp3s to one final mp3. Set it to NO if you want to study partial pieces for diagnosis purpose.
bga variable points to background music to be added via 7bgmp3.py.

4B) SCRIPTS EXPLANATION and EXECUTION. 

    In case of windows, Start the command prompt. Keep the book pdf files, BOOKNAME.PDF and all scripts together in same directory as they are working as such. 
    Also Ensure book filename is without spaces. 
    
 1. g_listvoices.py ## This will display available google cloud based voices and language codes. langcode and voicename environment vairalbes above are to be set based on outcome of this script depending on language of the book.

    This command will display all the google supported hindi indian voices.

    C:\books> g_listvoices.py | find /i "hi-in"   

 2a. pt.py ## Convert pdf to text. Google cloud APIs. 
 
 2b. ms_pt.py ## Convert pdf to text. MS Azure APIs.
 
 3a. 3wavv.py ## Convert text to wav voice file using google TextToSpeech SynthesizeLongAudioRequest api.
 
 3b. 0mp3ffmpeg.py ## use this if issues with 3wavv.py, this will use different (split files) logic and create mp3 instead uses Google cloud.
 
 4. ms_st4_wav.py ## wip. Creates wav file using Microsoft cognitive services.
    
 5. ms_listvoices.py ## List MS voices.
    
 7. 7bgmp3.py ## Add background music. There are lots of royalty free music available on internet. You can download any such mp3 and use it (see environment varriable bga above)
    
 8. requirements.txt ## install prereqs.
     
 9. .env sample file.
     
If there is heavy i/o (especially in 0mp3ffmpeg.py or st4, install arsenal and create ramdisk and work in ram based drive. Just copy back the final output to physical disk. This will give significant boost to performance.

ALTERNATE IDEAS:-

Instead of using 2pdftotxt.py, gimagereader (https://github.com/manisandro/gImageReader/releases/tag/master ) can be used for converting to txt from pdf. It is wonderful menu driven software. Internally it uses tesseract OCR engine.

Generated txt files from gimagereader can also be directly submitted to 3wavv.py or 0mp3ffmpeg.py. Just bring the .txt file in same directory and ensure proper environment variables are set.

MICROSOFT provides (old) software to convert text to wav. It's name is ttsapp. As I understand these aren't AI based.  Also check https://www.microsoft.com/en-us/download/details.aspx?id=10121.

