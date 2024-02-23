import sys
import os
import io
import re
import json
import shutil
## from google.cloud import texttospeech
from google.cloud import storage
from google.cloud import vision
## from google.cloud.vision import types

## from google.cloud import vision_v1 as vision
## from google.cloud.vision_v1 import types
import shutil

def pdf_to_text(input_fl , output_fl ):
            # Create a client for the Vision API
            client = vision.ImageAnnotatorClient()
            # Supported mime_types are: 'application/pdf' and 'image/tiff'
            mime_type = "application/pdf"
            client = vision.ImageAnnotatorClient()
            feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
            ## image_context={"language_hints": ["hi"]}
            image_context={"language_hints": [langhint]}
            with io.open(input_fl, 'rb') as pdf_file:
                 pdf_file=str(pdf_file)
                 storage_client = storage.Client(); bucket = storage_client.bucket(bktnm); 
                 ifl_in_cloud='pdf/'+str(input_fl) ; blob = bucket.blob(ifl_in_cloud) ## destination file name on cloud
                 generation_match_precondition = 0
                 if storage.Blob(bucket=bucket, name=ifl_in_cloud).exists(storage_client):
                     generation_match_precondition = blob.generation
                     blob.delete(if_generation_match=generation_match_precondition) ## delete if pre-exists
                 ofl_in_cloud='txt/'+str(output_fl) ;
                 if storage.Blob(bucket=bucket, name=ofl_in_cloud).exists(storage_client):
                     generation_match_precondition = blob.generation
                     blob.delete(if_generation_match=generation_match_precondition) ## delete if pre-exists
                 generation_match_precondition = 0
                 blob.upload_from_filename(input_fl, if_generation_match=generation_match_precondition) ## source file to read
                 print( f"File {input_fl} uploaded as {ifl_in_cloud}.")
                 ## upload is over. Prepare source and destination for pdf to text
                 gcs_source_uri     ="gs://"+os.environ['bktnm']+"/"+ifl_in_cloud; gcs_source=vision.GcsSource(uri=gcs_source_uri)
                 input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
                 gcs_destination_uri="gs://"+os.environ['bktnm']+"/"+"txt/"+output_fl
                 gcs_destination=vision.GcsDestination(uri=gcs_destination_uri)
                 output_config = vision.OutputConfig( gcs_destination=gcs_destination, batch_size=batch_size)
                 async_request = vision.AsyncAnnotateFileRequest(
                                    features=[feature], input_config=input_config, output_config=output_config, image_context=image_context
                                 )
                 operation = client.async_batch_annotate_files(requests=[async_request])

                 print("Waiting for the pdf to txt to finish..")
                 filesResponse=operation.result(timeout=420)
                 print(f"pdf to txt finished: Saved as {ofl_in_cloud}.");
                 write_to_text("gs://"+os.environ['bktnm']+"/"+"txt/",output_fl,ofl_in_cloud);
                 exit()

def write_to_text(gcs_destination_uri, output_fl, ofl_in_cloud):
    storage_client = storage.Client()

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1); prefix = match.group(2); bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix.
    ## print(prefix); 
    blob_list = list(bucket.list_blobs(prefix=prefix))
    print('Output files saving locally..')

    # Since we specified batch_size=100, first response contains upto first 100 pages of the input file.
    gen = (n for n in range(len(blob_list)) if output_fl in blob_list[n].name)
    if os.path.exists(output_fl): os.remove(output_fl) ## remove the output file if exists to open later as single file from one+ pages of one+ json files.
    for n in gen:
        blob =  blob_list[n]; json_file=re.sub(prefix,'',blob.name)  ## remove txt/
        print(f'{blob.name} as {json_file}, it will be overwritten if exists' )
        if os.path.exists(json_file): os.remove(json_file); 
        blob.download_to_filename(json_file)
        ## json_string = output.download_as_string()
        json_string = blob.download_as_bytes().decode("utf-8"); response = json.loads(json_string)
        # The actual response for the first page of the input file.
        print(f'Writing {n} set of pages of batch size: {batch_size} in {output_fl}..')
        for m in range(len(response['responses'])):

            first_page_response = response['responses'][m]

            try:
                annotation = first_page_response['fullTextAnnotation']
                context    = first_page_response['context']
                pg         = annotation['pages'] ; confidence = pg[0]['confidence']
            except(KeyError):
                print("No annotation for this page.")

            with open(output_fl, "a+", encoding="utf-8") as f:
             if pagenumbers=="YES" :
              f.write("\n=!pgB!="+'Page:'+str(context['pageNumber']).zfill(3).ljust(13,"=")+' Confidence:'+str(confidence).ljust(20,"=")+'Page:'+str(context['pageNumber']).zfill(3)+"=!Epg!=\n")
             f.write(annotation['text']);  
                 # f.write(annotation['text']+"\f"+u"\u000C")
                 # f.write(annotation['text']+u"\u000C")
              ## f.write(str(annotation['text'].encode("UTF-8")))
    print(f'{output_fl} saved.')

# Call the function
##input_dir = os.environ['input_dir']; output_dir = os.environ['output_dir'];
credential_path = os.environ['credential_path'] ; location = os.environ['location'] ; bktnm = os.environ['bktnm']; project_id = os.environ['project_id']
pagenumbers=os.environ['pagenumbers'];            langhint = os.environ['langhint']
batch_size = 100
pagenumbers=pagenumbers or "YES"
#async_detect_document("gs://ocr-test-wdc/document - 2021-01-15T202938.673.pdf", "gs://ocr-test-wdc/ocr_result ")
pdf_to_text(os.environ['book']+'.pdf',os.environ['book']+'.txt')
print(f'done.')




