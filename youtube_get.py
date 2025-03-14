# -*- coding: utf-8 -*-
"""youtube_get.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jHhqv2sk90OuFZ5fhyedk-vxQu1Tzoum
"""

#!pip install youtube_transcript_api
#!pip install sentencepiece
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
import nltk
import re
import numpy as np
from nltk.corpus import stopwords
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def youtube_sub(link):
  link=link
  video_id = link.split("=")[-1]
  text = YouTubeTranscriptApi.get_transcript(video_id,languages=["en"])
  subtitle = " ".join([x['text'] for x in text])

  return subtitle

def summarize_chunk(chunk,model_name = 't5-base'):
    # Load model and token
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    input_text = "summarize: " + chunk
    inputs = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=100, min_length=10, length_penalty=2.5, num_beams=5, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def chunk_and_summarize(text, chunk_size=300):
    tokens = tokenizer.encode(text)
    chunk_summaries = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunk_summary = summarize_chunk(chunk_text)
        chunk_summaries.append(chunk_summary)
    return " ".join(chunk_summaries)

# clean summary
def remove_redundant_sentences(text, similarity_threshold=.6):
    sentences = text.split('. ')
    vectorizer = TfidfVectorizer().fit(sentences)
    vectors = vectorizer.transform(sentences)
    matrix = cosine_similarity(vectors)

    unique_sentences = []
    for i in range(len(sentences)):
        if i in unique_sentences:
            continue
        unique = True
        for j in range(len(sentences)):
            if i != j and matrix[i, j] > similarity_threshold:
                unique = False
                break
        if unique:
            unique_sentences.append(sentences[i])

    return '. '.join(unique_sentences)

#put in sentence notation and parahraph format

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def capitalize_sentences_and_combine(text):
    sentences = sent_tokenize(text)
    capitalized_sentences = [sentence[0].upper() + sentence[1:] for sentence in sentences]
    combined_text = ' '.join(capitalized_sentences)
    return combined_text