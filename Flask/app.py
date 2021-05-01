#################### Module ####################
# Flask
from flask import Flask
from flask import request
from flask import send_file
from flask import make_response
from flask import render_template
from werkzeug.utils import secure_filename

# Pymongo
import pymongo

# Encrypt
import base64

# File
import bson
from bson import ObjectId
from bson.binary import Binary


#################### Init ####################
# Flask Settings
app = Flask(__name__)


# Pymongo Settings
connection = pymongo.MongoClient()
db = connection.db_name    # Database Name
file_meta = db.collection_name  # Database Collection Name

# No Cache
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


#################### Flask ####################
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get File Data
        file = request.files['file']

        # Save File
        file.save(secure_filename(file.filename))
        with open(file.filename, "rb") as f:
            encoded = Binary(f.read())

        # DB Insert File data
        file_meta.insert({"filename": file.filename, "file": encoded})
        return 'success'
    except:
        return 'fail'
    

@app.route('/download/<string:fileId>')
def download(fileId):
    # Find Database Field
    query = {'_id': ObjectId(fileId)}
    cursor = file_meta.find(query)

    # Get File
    fileName = cursor[0]['filename']

    # Download File
    return send_file(fileName, attachment_filename=fileName, as_attachment=True)


app.run(debug=True, host="0.0.0.0", port=80)
