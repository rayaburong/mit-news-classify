"""
Created Wednesday August 26 2020 21:15 +0700

@author: arunwpm
"""
import os

from mitnewsclassify import download, tfidf, tfidf_bi

import tensorflow as tf
import numpy as np
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
ld = None
id2tag = {}

def initialize( modelfile="model_ensemble.h5", 
                ldloc = 'labelsdict.p', #name of the labels dictionary generated by nb.py (should be labels_dict.csv)
                id2tagloc = 'nyt-theme-tags.csv' #name of the conversion table from tag id to tag name for NYTcorpus
                ):
    global model
    global ld
    global id2tag

    # get package directory
    pwd = os.path.dirname(os.path.abspath(__file__))
    pwd += "/data/ensemble/"
    if (not os.path.isdir(pwd)):
        answer = input("The model files have not been downloaded and the methods will not work. Would you like to download them? [y/n] ")
        if answer == 'y':
            download.download('ensemble')

    print("Initializing...")
    # initialize the trained model
    model = load_model(pwd + modelfile)
    print("Model...")
    
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
    vec0 = tfidf.getfeatures(txt)
    vec0 = np.concatenate((vec0, tfidf_bi.getfeatures(txt)), axis=1)
    # print(vec0)

    mat = model.predict(vec0)
    # print(mat)

    tags = []
    for i in range(len(mat[0])):
        if float(mat[0][i]) >= 0.5:
            tags.append(id2tag[ld[i]])
    # print(tags)

    return tags

if __name__ == "__main__":
    while True:
        txt = input("Enter text: ")
        gettags(txt)