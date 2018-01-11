#Program that handles uploading multiple text files and searching within those files
# change path to upload files

import sys
import os
from flask import Flask, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename

reload(sys)
sys.setdefaultencoding('utf8')

UPLOAD_FOLDER = '/home/akshay/flask_beginning/text_uploads/'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        print dict(request.files)
        filedict = dict(request.files)
        for i in filedict['file']:
            print i
            filename = secure_filename(i.filename)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
      <p><input type="file" name="file" multiple="" class="span3">
         <input type="submit" value="Upload">
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search/<query>')
def searching(query):
    occurances = {}
    primeOccurances = {}
    query = query.lower()
    words = query.split(' ')
    for item in os.listdir(UPLOAD_FOLDER):
        file = open(UPLOAD_FOLDER + item)
        flag = False
        indexes = []
        count = 1
        lines = file.readlines()
        for line in lines:
            line = line.lower()
            if query in line:
                flag = True
                indexes.append((count, line.index(query)))
            count+=1
        if flag is False:
            indexes = []
            count = 1
            for line in lines:
                for word in words:
                    if word not in ['a', 'an', 'the', 'if', 'of', 'it']:
                        if word in line:
                            indexes.append((count, line.index(word)))
                count += 1
            occurances[item] = indexes
        else:
            primeOccurances[item] = indexes
        # str1 = ' '.join(str(e) for e in indexes)
        # occurances[item] = str1
    return jsonify(primeOccurances)


if __name__ == '__main__':
	app.run(debug=True)
