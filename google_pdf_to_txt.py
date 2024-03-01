import json
import os
import re

from dotenv import load_dotenv
from google.cloud import storage, vision

load_dotenv()


credential_path = os.environ["credential_path"]
project_id = os.environ["project_id"]
location = os.environ["location"]
bktnm = os.environ["bktnm"]

book = os.environ["book"]
langhint = os.environ["langhint"]
pagenumbers = os.environ["pagenumbers"] or "YES"

batch_size = 100


def write_to_text(gcs_destination_uri, output_file, output_file_in_cloud):
    storage_client = storage.Client()

    match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    bucket = storage_client.get_bucket(bucket_name)

    blob_list = list(bucket.list_blobs(prefix=prefix))
    print("Output files saving locally..")

    ## remove the output file if exists to open later as single file from one+ pages of one+ json files.
    if os.path.exists(output_file):
        os.remove(output_file)

    gen = (n for n in range(len(blob_list)) if output_file in blob_list[n].name)
    for n in gen:
        blob = blob_list[n]
        json_file = re.sub(prefix, "", blob.name)  ## remove txt/
        print(f"{blob.name} as {json_file}, it will be overwritten if exists")
        if os.path.exists(json_file):
            os.remove(json_file)
        blob.download_to_filename(json_file)
        json_string = blob.download_as_bytes().decode("utf-8")
        response = json.loads(json_string)
        for m in range(len(response["responses"])):
            first_page_response = response["responses"][m]
            try:
                annotation = first_page_response["fullTextAnnotation"]
                context = first_page_response["context"]
                pg = annotation["pages"]
                confidence = pg[0]["confidence"]
            except KeyError:
                print("No annotation for this page.")

            with open(output_file, "a+", encoding="utf-8") as f:
                if pagenumbers == "YES":
                    f.write(f"\n=!pgB!=Page: {str(context['pageNumber']).zfill(3).ljust(13, '=')} Confidence: {str(confidence).ljust(20, '=')} Page: {str(context['pageNumber']).zfill(3)}=!Epg!=\n")
                f.write(annotation["text"])
    print(f"{output_file} saved.")

    with open(output_file, "r", encoding="utf-8") as f:
        text = f.read()
    return text


def pdf_to_text(input_file):
    output_file = input_file.split(".")[0] + ".txt"
    client = vision.ImageAnnotatorClient()
    mime_type = "application/pdf"  # Supported mime_types are: 'application/pdf' and 'image/tiff'
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION, model="builtin/latest")
    image_context = {"language_hints": [langhint]}

    storage_client = storage.Client()
    bucket = storage_client.bucket(bktnm)

    input_file_in_cloud = "pdf/" + str(input_file)
    blob = bucket.blob(input_file_in_cloud)  ## destination file name on cloud
    generation_match_precondition = 0

    ## delete if pre-exists
    if storage.Blob(bucket=bucket, name=input_file_in_cloud).exists(storage_client):
        generation_match_precondition = blob.generation
        blob.delete(if_generation_match=generation_match_precondition)

    output_file_in_cloud = "txt/" + str(output_file)
    ## delete if pre-exists
    if storage.Blob(bucket=bucket, name=output_file_in_cloud).exists(storage_client):
        generation_match_precondition = blob.generation
        blob.delete(if_generation_match=generation_match_precondition)

    generation_match_precondition = 0
    ## source file to read
    blob.upload_from_filename(input_file, if_generation_match=generation_match_precondition)  
    print(f"File {input_file} uploaded as {input_file_in_cloud}.")  

    ## upload is over. Prepare source and destination for pdf to text
    gcs_source_uri = "gs://" + bktnm + "/" + input_file_in_cloud
    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination_uri = "gs://" + bktnm + "/" + "txt/" + output_file
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature],
        input_config=input_config,
        output_config=output_config,
        image_context=image_context,
    )
    operation = client.async_batch_annotate_files(requests=[async_request])

    print("Waiting for the pdf to txt to finish..")
    filesResponse = operation.result(timeout=420)
    print(f"pdf to txt finished: Saved as {output_file_in_cloud}.")
    text = write_to_text(
        f"gs://{bktnm}/txt/",
        output_file,
        output_file_in_cloud,
    )
    return text


if __name__ == "__main__":
    pdf_to_text(book)
    print(f"done.")
