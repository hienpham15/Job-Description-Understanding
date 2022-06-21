#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:41:23 2022

@author: hienpham
"""
import argparse
import os
from glob import glob
from pdfminer.high_level import extract_text


parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    "-i",
                    help="Input files directory",
                    type=str)

parser.add_argument("--output",
                    "-o",
                    help="Ouput files directory",
                    type=str)

args = parser.parse_args()

#rawDataPath = r'/home/hienpham/Bureau/Job-Description-Understanding/raw_data/'
rawDataPath = args.input
outputDir = args.output
if not os.path.exists(outputDir):
    os.mkdir(outputDir)

pdfFiles = glob(rawDataPath + '*.pdf')

for file in pdfFiles:
    fileName = file.replace(rawDataPath, '').replace('.pdf', '')
    text = extract_text(file)
    with open(os.path.join(outputDir, fileName + '.txt'), 'w') as f:
        f.write(text)
