import os

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
bkin = os.environ["book"] + ".pdf"
bkout = os.environ["book"] + ".txt"

path_to_sample_documents = bkin
furl = "https://awgpsac.org/gp/" + bkin

document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
pagenumbers = os.environ["pagenumbers"] or "YES"

with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=f)
    result = poller.result()

text_content = ""
pageNumber = 1
for page in result.pages:
    confidence = 0.99999999
    text_content += f"\n=!pgB!=Page: {str(pageNumber).zfill(3).ljust(13, "=")} Confidence: {str(confidence).ljust(20, "=")} Page: {str(pageNumber).zfill(3)}=!Epg!=\n"

    for line in page.lines:
        text_content += line.content + "\n"
    pageNumber = pageNumber + 1

output_text_file = bkout
with open(output_text_file, "w", encoding="utf-8") as output_file:
    output_file.write(text_content)

print(f"Text extracted from PDF (in Hindi) and saved to {output_text_file}")
