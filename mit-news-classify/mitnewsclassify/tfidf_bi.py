"""
Created Wednesday August 19 2020 20:44 +0700

@author: arunwpm
"""
import os

from mitnewsclassify import download

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model

import traceback
import csv
import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

def loadcsv(filename):
    with open(filename, newline='') as f: 
        return list(csv.reader(f))

model = None
cntVecr = None
tfmer = None
ld = None
id2tag = {}

def initialize( modelfile="model_2000_500_50.h5", 
                vocabfile="small_vocab_bi_20.csv",
                tfmerfile="tfmer_bi_20.p",
                ldloc = 'labelsdict_bi_20.p', #name of the labels dictionary generated by nb.py (should be labels_dict.csv)
                id2tagloc = 'nyt-theme-tags.csv' #name of the conversion table from tag id to tag name for NYTcorpus
                ):
    global model
    global cntVecr
    global tfmer
    global ld
    global id2tag

    # get package directory
    pwd = os.path.dirname(os.path.abspath(__file__))
    pwd += "/data/tfidf_bi/"
    if (not os.path.isdir(pwd)):
        answer = input("The model files have not been downloaded and the methods will not work. Would you like to download them? [y/n] ")
        if answer == 'y':
            download.download('tfidf_bi')

    print("Initializing...")
    # initialize the trained model
    model = load_model(pwd + modelfile)
    print("Model...")
    
    # initialize the count vectorizer
    vocab = loadcsv(pwd + vocabfile)
    vocab = [x[0] for x in vocab] # extra layer of list that we don't want here
    cntVecr = CountVectorizer(vocabulary=vocab, ngram_range=(2,2))
    print("Count Vectorizer...")

    # initialize the tfidf transformer
    with open(pwd + tfmerfile, "rb") as tfmerin:
        tfmer = pickle.load(tfmerin)
    print("TF-IDF Transformer...")
    
    # initialize the matrix index -> tag id file and the tag id -> tag name file
    with open(pwd + ldloc, "rb") as ldin:
        ld = pickle.load(ldin)
    # ld = loadcsv(pwd + ldloc)
    id2tag_table = loadcsv(pwd + id2tagloc)
    for row in id2tag_table:
        if row == []:
            continue
        id2tag[row[1]] = row[2]
    print("Miscellaneous...")

def gettags(txt):
    if (model is None):
        initialize()
    vec0 = cntVecr.transform([txt])
    vec1 = tfmer.transform(vec0)
    # print(vec1)

    mat = model.predict(vec1.todense())
    # print(mat)

    tags = []
    for i in range(len(mat[0])):
        if float(mat[0][i]) >= 0.5:
            tags.append(id2tag[ld[i]])
    # print(tags)

    return tags

def getfeatures(txt):
    if (model is None):
        initialize()
    vec0 = cntVecr.transform([txt])
    vec1 = tfmer.transform(vec0)
    # print(vec1)

    extractor = keras.Model(inputs=model.input, outputs=model.get_layer('last_hidden').output)
    features = extractor(vec1.todense())
    # print(mat)

    return features

def free():
    global model
    del model
    global cntVecr
    del cntVecr
    global tfmer
    del tfmer

if __name__ == "__main__":
    while True:
        txt = input("Enter text: ")
        gettags(txt)