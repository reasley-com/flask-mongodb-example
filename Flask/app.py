#################### Module ####################
# Flask
from flask import Flask
from flask import request
from flask import send_file
from flask import url_for
from flask import redirect
from flask import flash
from flask import make_response
from flask import render_template
from werkzeug.utils import secure_filename

# Pymongo
import pymongo
import gridfs


# Encrypt
import base64

# File
import bson
from bson import ObjectId
from bson.binary import Binary


#################### Init ####################
# Flask Settings
app = Flask(__name__)
app.secret_key = 'reasley'


# Pymongo Settings
connection = pymongo.MongoClient()  # Mongo DB Client Connection
db = connection.db_name             # Database Name

normal_meta = db.collection_name    # Database Collection Name
grid_meta   = db.fs.files           # Database Collection Name

fs          = gridfs.GridFS(db)     # GRIDFS Settings

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
    normal_list = normal_meta.find()
    grid_list   = grid_meta.find()
    return render_template('index.html', normal_list=normal_list, grid_list=grid_list)

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
        normal_meta.insert({"filename": file.filename, "file": encoded})
        
        flash('success')
        return redirect(url_for('index'))
    except:
        flash('fail')
        return redirect(url_for('index'))

@app.route('/download/<string:fileId>')
def download(fileId):
    # Find Database Field
    query = {'_id': ObjectId(fileId)}
    cursor = normal_meta.find(query)

    # Get File
    fileName = cursor[0]['filename']

    # Download File
    return send_file(fileName, attachment_filename=fileName, as_attachment=True)



@app.route('/gridfs_upload', methods=['POST'])
def gridfs_upload():
    try:
        # Get File Data
        file = request.files['file']

        # Save File
        file.save(secure_filename(file.filename))
        with open(file.filename, "rb") as f:
            encoded = Binary(f.read())

        # DB Insert File data
        res = fs.put(encoded, filename=file.filename)
        flash('success')
        return redirect(url_for('index'))
    except:
        flash('fail')
        return redirect(url_for('index'))

    

@app.route('/gridfs_download/<string:fileId>')
def gridfs_download(fileId):
    # Find File
    filedId = ObjectId(fileId)
    file = fs.get(filedId)

    # Download File
    return send_file(file, attachment_filename=file.filename, as_attachment=True)


app.run(debug=True, host="0.0.0.0", port=80)
