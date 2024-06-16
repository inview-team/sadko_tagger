import sys
import os
import csv
import shutil
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words_en = set(stopwords.words('english'))
stop_words_ru = set(stopwords.words('russian'))

def clean_text(text, language='english'):
    text = text.lower()  
    text = re.sub(r'\d+', '', text)  
    text = re.sub(r'\s+', ' ', text) 
    text = re.sub(r"[#]+", "", text) 
    text = re.sub(r'[^\w\s]', '', text)  
    
    words = word_tokenize(text)  
    
    if language == 'russian':
        stop_words = stop_words_ru
    else:
        stop_words = stop_words_en
    
    words = [word for word in words if word not in stop_words]  
    return ' '.join(words)

def extract_terms(description):
    terms = re.findall(r"#\w+|\w+", description)
    normalized_terms = [term.lower() for term in terms]
    return normalized_terms