These are set of scripts that will help to convert scanned pdf (such as old books) to UTF-8 based text files. Once you finish editing text files with appropriate corrections, it will also help to create audio file either MP3 or .WAV (linear16). This project is made and tested on windows but doesn't look like there is any specific dependency on operating system and hopefully should work on unix environments as well. 

While this is tested with English and Hindi/Sanskrit texts; it is expected to work on other UTF-8 based files too as long as it is supported by google cloud vision and TextToSpeech libraries.

PROJECT IS NOT TESTED WITH UNIX/LINUX environments. But could work with minimal changes ( enviroent variable setup in bash needs different syntax then the one in README or in sample envcmd.cmd file)


While looking for converting scanned pdfs to audio, could not find good complete solution. This project uses Google provided neural voices and it is flexible to allow for language and voice selection as google continues to releases new voices with ongoing improvements in AI.


PREREQS:

Users must have good or advanced knowledge of operating system commands etc.

Must have google cloud account with storage bucket, project id, location and application credentials json file.

Install:- Python 3.12, Google cloud client libraries for Vision + TextToSpeech + Storage. and ffmpeg (and available path).

set the emvironment variables as follows (See envcmd.cmd) :- 

4A) REM book_file_name below should be without extension and avoid spaces in filename (rename otherwise). For example, if Book File Name is BE_HAPPY.PDF then set book=BE_HAPPY scripts will automatically create BE_HAPPY.txt , BE_HAPPY.wav , BE_HAPPY.mp3 , BE_HAPPY.json etc using BE_HAPPY.PDF. Actual Source file MUST have .PDF extension. 

set book=book_file_name_without_extension 

set GOOGLE_APPLICATION_CREDENTIALS=C:/final_pre/gogtts/gcreds.json 

set credential_path=%GOOGLE_APPLICATION_CREDENTIALS% 

set project_id=gprojid 

set location=us-west1 

set bktnm=bucketname 

set langcode=en-IN 

set voicename=en-IN-Neural2-C 

set speakingrate=0.85 

REM Pagenumbers are inserted into text file to help compare with .pdf during verification and corrections in text file for manual post scan compariosn. 

set pagenumbers=YES 

set sentstop=� 

set removepartial=YES


In Linux/Unix world (bash shell) , export will be used instead of set command above (with credential_path variable assignment will have $ sign instead of first % sign and last % sign will need to be removed). 
REM command (remark) will be converted to # as a replacement for comment beginner identifier. 

sentstop variable is sentence stop character. It can be different in different languages. It has been tested with hindi language. It is used in buffered mp3 creation. (when TextToSpeechLongAudioSynthesizeClient api fails)

removepartial variable helps diagnose if mp3 generator fails to merge partial mp3s to one final mp3. Set it to NO if you want to study partial pieces for diagnosis purpose.

4B) SCRIPTS EXPLANATION and EXECUTION. 
 0. Start the command prompt and set the environment and goto respective directory. Keep the book pdf files, BOOKNAME.PDF and all scripts together in same directory as they are working as such. 
    Also Ensure book filename is without spaces. 
 1. listvoices.py ## This will display available google cloud based voices and language codes. langcode and voicename environment vairalbes above are to be set based on outcome of this script depending on language of the book.

    This command will display all the google supported hindi indian voices.

    C:\books>  listvoices.py | find /i "hi-in"   

 2. 2pdftotxt.py  ## Convert pdf to text file using google vision apis. 
 3. 3wavv.py      ## Convert txt to wav voice file using google TextToSpeech SynthesizeLongAudioRequest api. This seems WIP by google. 
 4. 0mp3ffmpeg.py ## Convert txt to mp3 voice file using google TextToSpeech synthesize_speech api.


If there is an heavy i/o (especially in 0mp3ffmpeg.py, imdisk can be used for creating ramdisk and work in ram. Only copy back the final output to physical disk. This will give significant boost to performance.

ALTERNATE IDEAS:-

Instead of using 2pdftotxt.py, gimagereader (https://github.com/manisandro/gImageReader/releases/tag/master ) can be used for converting to txt from pdf. It is wonderful menu driven software. Internally it uses tesseract OCR engine.
Generated txt files from gimagereader can also be directly submitted to 3wavv.py or 0mp3ffmpeg.py. Just bring the .txt file in same directory and ensure proper environment variables are set.

MICROSOFT provides (old) software to convert text to wav. It's name is ttsapp. As I understand these aren't AI based.  Also check https://www.microsoft.com/en-us/download/details.aspx?id=10121.



