#COMP-3110, Final Project, Step 1 : Preprocessing implementation
#preprocess.py
#Author : Munmeet Grewal


import re
from typing import List

WHITESPACE_RUN = re.compile(r"\s+") 

def remove_whitespace(text: str)-> str :
  return WHITESPACE_RUN.sub(" ", text)

def cleanUp_line(raw_line: str) -> str:
  line = raw_line.rstrip("\n\r")
  line = line.lower()
  line = line.strip()
  if line:
    line = remove_whitespace(line)
  return line

def preprocess_lines(lines: list[str]) -> list[str]: 
  cleaned = []
  for l in lines:
    c = cleanUp_line(l)
    # Keep all lines, even empty ones (normalized)
    cleaned.append(c)
  return cleaned

def preproc_from_disk(path:str, encoding: str = "utf-8") -> List[str]:
  with open(path, "r", encoding=encoding) as f:
    return preprocess_lines(f)

if __name__ == "__main__":
  import sys
  
  if len(sys.argv) != 2: 
    print("Error: Incorrect number of files provided")
    sys.exit(1)

  file_path = sys.argv[1]
  cleanedUp_lines = preproc_from_disk(file_path)
  for i, line in enumerate(cleanedUp_lines, start = 1):
    print(f"{i:4}: {line}") 
  
