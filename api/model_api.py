#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 10:24:22 2022

@author: hienpham
"""
import uvicorn
import random
from fastapi import FastAPI
#from typing import Union
from pydantic import BaseModel

# =============================================================================
# app = FastAPI()
# 
# @app.get("/")
# 
# def read_root():
#     return {"Hello": 'World'}
# 
# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
# =============================================================================



def load_model(params='test'):
    """
    This is where we load NLP model
    Parameters
    ----------
    **params : Parameters.

    Returns
    -------
    model.

    """
    titles = ['DS', 'DE', 'DA']
    return random.choice(titles), len(params)



class EmailIn(BaseModel):
    text = 'Checking reponse'
    model_language = "en"
    
    
class RelevanceOut(BaseModel):
    job_title: str
    score: float


app = FastAPI()
@app.get("/")
def root():
    return {"Message": "model API ready to deploy"}


@app.post("/relevance", response_model=RelevanceOut)
def getScore(user_requests: EmailIn):
    text_to_analyse = user_requests.text

    language = user_requests.model_language
    #title = 'DE'

    title, score = load_model(text_to_analyse)
    return {"job_title": title, "score": score}

