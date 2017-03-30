import os
import nltk
import json
from flask import Flask
from flask import request
from summarizer import summarize
import keyword_extraction as kp


app = Flask(__name__, static_url_path='', static_folder='.')



@app.route('/summarize', methods=['GET', 'POST'])
def summarize_route():
    """
    Flask route for summarization + noun phrases task
    :return: Json summary response
    """
    if 'file' not in request.files:
        return 'no file provided'
    file = request.files['file']
    if file.filename == '':
        return 'no file provided'
    if file:
        # filename = secure_filename(file.filename)
        src = os.getcwd() + '/uploaded_data/'
        file.save(os.path.join(src, file.filename))

    columns = request.form['columns'].split('%')
    l = int(request.form['l-value'])
    k = int(request.form['top-k'])
    form_use_bigrams = request.form['use-bigrams']
    form_use_svd = request.form['use-svd']
    form_use_noun_phrases = request.form['use-noun-phrases']
    form_split_longer_sentences = request.form['split-longer-sentences']
    form_split_length = request.form['to-split-length']
    form_group_by = request.form['group-by']
    form_extract_sibling_sents = request.form['extract-sibling-sents']

    use_bigrams = strtobool(form_use_bigrams)
    use_svd = strtobool(form_use_svd)
    use_noun_phrases = strtobool(form_use_noun_phrases)
    split_longer_sentences = strtobool(form_split_longer_sentences)
    extract_sibling_sents = strtobool(form_extract_sibling_sents)

    summary = summarize(
        data=file.filename, columns=columns, group_by=form_group_by,
        l=l,
        use_bigrams=use_bigrams,
        use_svd=use_svd, k=k,
        use_noun_phrases=use_noun_phrases,
        split_longer_sentences=split_longer_sentences, to_split_length=int(form_split_length),
        extract_sibling_sents=extract_sibling_sents
    )

    return json.dumps(summary)



@app.route('/keyphrases', methods=['GET', 'POST'])
def return_keyphrases():
    
    print request.files
    if 'file-keyphrase' not in request.files:
        return 'no file provided'
    file = request.files['file-keyphrase']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return 'no file provided'
    if file:
        # filename = secure_filename(file.filename)
        src = os.getcwd() + '/uploaded_data/'
        file.save(os.path.join(src, file.filename))
    
    nb_kp = request.form['nb_keyphrases']
    min_char_length = request.form['min_char_length']
    max_words_length = request.form['max_words_length']
    min_keyword_frequency = request.form['min_keyword_frequency']
    
    keyphrases = kp.extract_keyphrases(
                                       filename='uploaded_data/'+file.filename,
                                       nb_kp=nb_kp,
                                       min_char_length=min_char_length,
                                       max_words_length=max_words_length,
                                       min_keyword_frequency=min_keyword_frequency)
                                       
    return json.dumps(keyphrases)


def strtobool (val):
    """
    Copied from https://github.com/python-git/python/blob/master/Lib/distutils/util.py
    Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = str.lower(str(val))
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise(ValueError, "invalid truth value %r" % (val,))



if __name__ == '__main__':
    # Install nltk tools on Heroku
    if os.environ.get('HEROKU'):
        nltk.download('wordnet')
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')

    env_port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=env_port, debug=True)
