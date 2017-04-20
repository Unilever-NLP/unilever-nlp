from __future__ import absolute_import
from __future__ import print_function

import pandas as pd
import rake
import json
import numpy as np


def extract_keyphrases_survey(filename, nb_kp, min_char_length, max_words_length, min_keyword_frequency, groupby, headers):
    
    
    nb_kp = int(nb_kp)
    srv_raw = pd.ExcelFile(filename)
    srv = srv_raw.parse()
    
    if len(headers) == 0:
        del srv[list(srv)[0]]
        qst = list(srv)
        qst = [str(q).split("\n")[0] for q in list(srv)]
        srv.columns = qst
    else:
        qst = headers.split('%')
        cols = [q.strip('\n') for q in srv.columns]
        srv.columns = cols
    
    srv_concat = [reduce(lambda x,y: str(x)+'. '+str(y), srv[qst[k]]) for k in range(len(qst))]
    
    stoppath = "SmartStoplist.txt"
    '''
        Arguments:
        stoppath: path to the list of stopwords
        int1 (1): min_char_length, minimum number of characters per word
        int2 (5): max_words_length, maximum number of words per keyphrase
        int4 (1): min_keyword_frequency, minimum nb of occurences for the keyword in the text.
    '''
    rake_object = rake.Rake(stoppath, int(min_char_length), int(max_words_length), int(min_keyword_frequency))
    keyphrases = {qst[k]: rake_object.run(srv_concat[k]) for k in range(len(qst))}
    
    key_scores = {key:[ct for (kw, ct) in keyphrases[key]] for key in keyphrases.keys()}
    scaler_dic = {key:{'min':np.min(key_scores[key]),'max':np.max(key_scores[key]), 'delta': np.max(key_scores[key])-np.min(key_scores[key])} for key in keyphrases.keys()}
    
    keyphrases = {qst:[(kw, "%.2f" % ((ct-scaler_dic[qst]['min'])/scaler_dic[qst]['delta'])) for (kw,ct) in lst][:nb_kp] for (qst,lst) in keyphrases.iteritems()}    
    
    keyphraz = {'Keyphrase extraction':keyphrases}
    return keyphraz


def extract_keyphrases_reviews(filename, nb_kp, min_char_length, max_words_length, min_keyword_frequency, groupby, headers):
    
    nb_kp = int(nb_kp)
    stoppath = "SmartStoplist.txt"
    
    with open('product_name.json', 'r') as f:
        product_names = json.load(f)
    
    
    data = pd.read_excel(filename)
    
    if len(groupby) == 0:
        groupby = 'productID'        
    
    if len(headers) == 0:
        columns_to_keep = list(data.columns)
        columns_to_extract = list(data.columns)
        columns_to_extract.remove(groupby)
        cols = [q.strip('\n') for q in data.columns]
        data.columns = cols
        
    else:   
        columns_to_extract = headers.split('%')
        columns_to_keep = [groupby]+columns_to_extract
        cols = [q.strip('\n') for q in data.columns]
        data.columns = cols
    
    
        
    data = data[columns_to_keep]
    
    product_reviews = {col: {prod:'' for prod in set(data[groupby])} for col in columns_to_extract}
    
    keyphraz = {col:{} for col in columns_to_extract}
    
    for col in columns_to_extract:
        for k in range(len(data)):
            product_reviews[col][data[groupby][k]]+= '. '+str(data[col][k])
    
        rake_object = rake.Rake(stoppath, int(min_char_length), int(max_words_length), int(min_keyword_frequency))
        keyphrases = {product: rake_object.run(review) for (product, review) in product_reviews[col].iteritems()}
        
        key_scores = {key:[ct for (kw, ct) in keyphrases[key]] for key in keyphrases.keys()}
        
        if len(min(keyphrases.values())) == 0:
            keyphrases = {str(product_names[prod_id]):[('Impossible to extract keywords',0.0) for (kw,ct) in lst][:nb_kp] for (prod_id,lst) in keyphrases.iteritems()}
        else:
            scaler_dic = {key:{'min':np.min(key_scores[key]),'max':np.max(key_scores[key]), 'delta': np.max(key_scores[key])-np.min(key_scores[key])} for key in keyphrases.keys()}
            keyphrases = {str(product_names[prod_id]):[(kw, "%.2f" % ((ct-scaler_dic[prod_id]['min'])/scaler_dic[prod_id]['delta'])) for (kw,ct) in lst][:nb_kp] for (prod_id,lst) in keyphrases.iteritems()}    
        
        keyphraz[col] = keyphrases
    
    return keyphraz


