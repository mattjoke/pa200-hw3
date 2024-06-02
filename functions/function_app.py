import io
import azure.functions as func
import logging
from PIL import Image
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="image-queue",
                               connection="AzureWebJobsStorage") 
def BlobTrigger1(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    file_name = myblob.get_body().decode('utf-8')
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    container_name = "photos"
    
    # Download the original image
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    blob_data = blob_client.download_blob().readall()
    
    # Open the image and perform resizing
    image = Image.open(io.BytesIO(blob_data))
    resized_image = image.resize((800, 600))
    
    # Save the resized image to a bytes buffer
    byte_arr = io.BytesIO()
    resized_image.save(byte_arr, format='JPEG')
    byte_arr = byte_arr.getvalue()
    
    # Upload the resized image back to Blob Storage
    resized_blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"resized-{file_name}")
    resized_blob_client.upload_blob(byte_arr, overwrite=True)

    # Remove the original image from the queue
    queue_blob_client = blob_service_client.get_blob_client(container="image-queue", blob=file_name)
    queue_blob_client.delete_blob()
    
    logging.info(f'Resized image saved as resized-{file_name}')