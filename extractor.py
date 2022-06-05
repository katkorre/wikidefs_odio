from sentence_splitter import SentenceSplitter, split_text_into_sentences
from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, TextClassificationPipeline, DataCollatorWithPadding, AutoModelForSequenceClassification
import numpy as np
from datasets import load_metric
import pandas as pd
from operator import itemgetter
import os


#choose a path to get a file
path_to_text = "/home/akorre/wiki_files/it"

def run(f):
  splitter = SentenceSplitter(language='el')
  #open file, sentencize and create list of sentences
  #with open(path_to_text, 'r') as f:
  f = f.read()
  sentences = splitter.split(text=f)

  checkpoint = 'bert-base-multilingual-cased'
  tokenizer = AutoTokenizer.from_pretrained(checkpoint)
  model = AutoModelForSequenceClassification.from_pretrained('/home/akorre/huggingface/it')

  pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)

  #predictions = pipe(subdump_list)
  predictions = pipe(sentences)

  final_scores = []
  n=0

  #print highest score in list of sentences using pre-trained model bert trained with Navigli's corpus
  for idx, sentence in enumerate(sentences):
      scores = predictions[idx][1]['score']
      if scores >= 0.6:
          n = n + 1
          final_scores.append((sentence, scores))
          if n == 2:
              break

  return final_scores

for filename in os.listdir(path_to_text):
    if filename.endswith('.txt'):
        with open(os.path.join(path_to_text, filename)) as f:
            print(run(f))
