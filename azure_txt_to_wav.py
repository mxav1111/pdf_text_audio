import os
import re

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


def list_ms_voices():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["SPEECH_KEY"],
        region=os.environ["SPEECH_REGION"],
    )
    client = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    voices_result = client.get_voices_async().get()
    print("Voice:")
    for v in voices_result.voices:
        print(f"Name:{v.name}|{v.short_name}|{v.locale}|{v.gender}|{v.local_name}|{v.voice_type}|{v.style_list}")


def split_text_into_chunks(text, max_chunk_size):
    sentstop = os.environ["sentstop"]
    text = text.replace("\n", "")
    sentences = text.split(sentstop)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + sentstop
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + sentstop

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def text_to_mp3_chunk(text, output_filename):
    speech_key = os.environ["SPEECH_KEY"]
    service_region = os.environ["SPEECH_REGION"]

    chunks = split_text_into_chunks(text, max_chunk_size=500)  # 500 in bytes
    print(f' {speech_key} | {service_region} | {os.environ["msvoicename"]} ')
    for i, chunk in enumerate(chunks):
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=service_region
        )
        speech_config.speech_synthesis_voice_name = os.environ["msvoicename"]
        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=f"{output_filename}_{i}.wav"
        )
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        result = synthesizer.speak_text_async(chunk).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for chunk [{chunk}], and the audio was saved to [{output_filename}_{i}]")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")


def main():
    input_text_file = os.environ["book"] + ".txt"
    output_directory = "output_mp3_chunks"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_text_file, "r", encoding="utf-8") as file:
        fc = file.read()

    fc = re.sub(r"(?:=!pgB!=.*=!Epg!=\n)+", r"", fc)
    fc = re.sub(r"\([^ ]\)-(\n)+", r"\1", fc)
    fc = re.sub(r"([^ ])-\n", r"\1", fc)
    fc = re.sub(r"(\n)+", r" ", fc)
    fc = re.sub(r"\n", r" ", fc)
    fc = re.sub(r"[ ][ ]*", r" ", fc)

    text_to_mp3_chunk(fc, os.path.join(output_directory, "output"))


if __name__ == "__main__":
    main()
