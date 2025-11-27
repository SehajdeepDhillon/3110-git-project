#COMP-3110, Final Project, Step 1 : Preprocessing implementation
#preprocess.py
#Author : Munmeet Grewal


import rec
from typing import Iterable, List

WHITESPACE_RUN = re.compile(r"\st") 

def remove_whitespace(text: str)-> str :
  return WHITESPACE_RUN.sub(" ", text)

def cleanUp_line(raw_line: str) -> str:
  line = 
