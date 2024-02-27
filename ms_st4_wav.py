import os
import re
import azure.cognitiveservices.speech as speechsdk
from   dotenv import load_dotenv
load_dotenv()

def split_text_into_chunks(text, max_chunk_size):
    # Split the text into chunks based on sentence endings
    sentstop=os.environ["sentstop"]
    #text      = text.replace('\x0d\x0a','')
    # text      = text.replace('\r','')
    text      = text.replace('\n','')
    sentences = text.split(sentstop)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            #current_chunk += sentence + '. '
            current_chunk += sentence + sentstop
        else:
            #current_chunk = sentence + '. '
            # current_chunk += sentence + sentstop
            chunks.append(current_chunk.strip())
            current_chunk = sentence + sentstop

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def text_to_mp3_chunk(text, output_filename):
    speech_key     = os.environ["SPEECH_KEY"]  # Replace with your actual subscription key
    service_region = os.environ["SPEECH_REGION"]  # Replace with your actual region

    chunks = split_text_into_chunks(text, max_chunk_size=500)  # 500 in bytes
    print(f' {speech_key} | {service_region} | {os.environ["msvoicename"]} ')
    for i, chunk in enumerate(chunks):
         #audio_config = speechsdk.audio.AudioOutputConfig(filename=f"{output_filename}_{i}.mp3", format=speechsdk.OutputFormat(mp3_bitrate=128))
         speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
         # speech_config.speech_synthesis_language   = os.environ["mslangcode"]  # Set the desired language
         speech_config.speech_synthesis_voice_name = os.environ["msvoicename"]  # Choose a voice
         audio_config       = speechsdk.audio.AudioOutputConfig(filename=f"{output_filename}_{i}.wav")
         synthesizer        = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
         result             = synthesizer.speak_text_async(chunk).get()
         ##print(chunk)
         ##print("DONE...")
         if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for chunk [{}], and the audio was saved to [{}_{}]".format(chunk, output_filename,i))
         elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))


         #if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
         #   print(f"Converted chunk {i + 1} to {output_filename}_{i}.mp3")

def main():
    input_text_file = os.environ["book"]+".txt"
    output_directory = 'output_mp3_chunks'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_text_file, 'r', encoding='utf-8') as file:
        fc = file.read()

    fc=re.sub(r'(?:=!pgB!=.*=!Epg!=\n)+',r'',fc)
    fc=re.sub(r'\([^ ]\)-(\n)+',r'\1',fc) ## word that splits and spans line using hypen is merged
    fc=re.sub(r'([^ ])-\n',r'\1',fc) ## remove new lines and convert multi spaces to single.
    fc=re.sub(r'(\n)+',r' ',fc); fc=re.sub(r'\n',r' ',fc); fc=re.sub(r'[ ][ ]*',r' ',fc)  ## remove new lines and convert multi spaces to single.
    text_to_mp3_chunk(fc, os.path.join(output_directory, 'output'))

if __name__ == "__main__":
    main()

