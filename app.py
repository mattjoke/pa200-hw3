import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
blob_service = BlobServiceClient.from_connection_string(os.environ['AZURE_STORAGE_CONNECTION_STRING'])
blob_name= 'image-queue'
blob_result_name = 'image-result'

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/result/<filename>')
def result(filename):
    url = f"https://{os.getenv('AZURE_STORAGE_ACCOUNT_NAME')}.blob.core.windows.net/{blob_result_name}/resized-{filename}"
    # Check if the file exists in the container
    if not blob_service.get_blob_client(blob_name, f"resized-{filename}").exists():
        return render_template('processing.html', filename=filename)
    return render_template('result.html', url=url)

@app.route('/push', methods=['POST'])
def push_post():
    file = request.files['file']
    random_substr = os.urandom(6).hex()
    filename = f"{random_substr}-{file.filename}"
    if not file:
        return redirect(url_for('err'))
    blob_service.get_blob_client(blob_name, filename).upload_blob(file)
    return render_template('processing.html', filename=filename)
    
@app.route('/err')
def err():
    return render_template('err.html')
    

if __name__ == '__main__':
   app.run()








