import os
import json
import distutils
from flask import Flask
from flask import request
from summarizer import summarize


app = Flask(__name__, static_url_path='', static_folder='.')


@app.route('/summarize', methods=['GET', 'POST'])
def hello_world():

    if 'file' not in request.files:
        return 'no file provided'
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return 'no file provided'
    if file:
        # filename = secure_filename(file.filename)
        src = os.getcwd() + '/uploaded_data/'
        file.save(os.path.join(src, file.filename))

    columns = request.form['columns'].split('%')
    l = int(request.form['l-value'])
    form_use_bigrams = request.form['use-bigrams']
    use_bigrams = distutils.util.strtobool(form_use_bigrams)

    summary = summarize(file.filename, columns, l, use_bigrams)
    return json.dumps(summary)


if __name__ == '__main__':
    # summary = summarize('survey_data.xlsx', ['What is Healthy Skin?', 'How do you know your skin is healthy?'])
    app.run() #host=HOST, port=PORT, debug=debug, threaded=threaded)
