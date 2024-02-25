from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv
load_dotenv()

# Replace with your own values
endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
bkin=os.environ['book']+'.pdf';bkout=os.environ['book']+'.txt'
## pdf_to_text(os.environ['book']+'.pdf',os.environ['book']+'.txt')
path_to_sample_documents = bkin
furl="https://awgpsac.org/gp/" + bkin
# Create a Document Intelligence client
document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
pagenumbers=os.environ['pagenumbers']; pagenumbers=pagenumbers or "YES"

## az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
## az cognitiveservices account show --name "1s" --resource-group "r1" --query "properties.endpoint"
## az cognitiveservices account show --name "r1di1" --resource-group "r1" --query "properties.endpoint"
## az cognitiveservices account keys list --name "r1di1" --resource-group "r1"

# Read the PDF document (specify language as Hindi)
with open(path_to_sample_documents, "rb") as f:
     ## poller = document_analysis_client.begin_analyze_document("prebuilt-layout", analyze_request=f, content_type="application/octet-stream", language="hi")
      poller = document_analysis_client.begin_analyze_document("prebuilt-read", document=f)
      result = poller.result()

## result: AnalyzeResult = poller.result()
result = poller.result()

# Extract text from the result
text_content = ""
pageNumber=1
for page in result.pages:
    confidence=0.99999999
    text_content += "\n=!pgB!="+'Page:'+str(pageNumber).zfill(3).ljust(13,"=")+' Confidence:'+str(confidence).ljust(20,"=")+'Page:'+str(pageNumber).zfill(3)+"=!Epg!=\n"
    ## f.write("\n=!pgB!="+'Page:'+str(pageNumber).zfill(3).ljust(13,"=")+' Confidence:'+str(confidence).ljust(20,"=")+'Page:'+str(pageNumber).zfill(3)+"=!Epg!=\n")
    for line in page.lines:
        text_content += line.content + "\n"
    pageNumber=pageNumber+1

# Write the extracted text to a text file (UTF-8 compliant)
output_text_file = bkout
with open(output_text_file, "w", encoding="utf-8") as output_file:
    output_file.write(text_content)

print(f"Text extracted from PDF (in Hindi) and saved to {output_text_file}")

