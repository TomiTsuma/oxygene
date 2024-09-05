from fastapi import FastAPI, HTTPException, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from text_classification import classifyText

class TextClassifier(BaseModel):
    sequence: str = "Rafael Nadal is probably the best tennis player ever"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/text-classication")
def classify_text(textClassifier : TextClassifier):
    return classifyText(textClassifier.sequence)