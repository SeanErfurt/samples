# coding: utf-8

# Author: Sean Erfurt

#how often the top ranked candidates match the test data, grouped in terms
# of the percentage of correct individual forms, and the percentage of
# entire correct paradigms

# TODO: add full-paradigm scores

# File Format Examples													#
'''
Gold:
vloei+VPRS* vloei
vloei+VPRS* vloeiende
VPST*+vloei+VPST*   gevloei
herken+VPRS*    herken
herken+VPRS*    herkennende
herken+VPST*    herken
...

Reranked:
10.191317105364678  v|l|o|e|i|+VPRS*|   v|l|o|e|i|_|
8.85360610057125    v|l|o|e|i|+VPRS*|   v|l|o|e|e|_|
8.101821761700927   v|l|o|e|i|+VPRS*|   v|l|o|e|i|ende|
8.481767668158573   v|l|o|e|i|+VPRS*|   v|l|o|e|o|_|
8.37277993506041    v|l|o|e|i|+VPRS*|   v|l|o|e|_|_|
8.35691886128588    v|l|o|e|i|+VPRS*|   v|l|o|e|ï|_|
8.324563677532955   v|l|o|e|i|+VPRS*|   v|l|o|e|in|_|
7.784302446215115   v|l|o|e|i|+VPRS*|   v|l|o|w|i|_|
7.765452034811237   v|l|o|e|i|+VPRS*|   v|l|o|ë|i|_|
10.191317105364678  v|l|o|e|i|+VPRS*|   v|l|o|e|i|_|
8.85360610057125    v|l|o|e|i|+VPRS*|   v|l|o|e|e|_|
8.101821761700927   v|l|o|e|i|+VPRS*|   v|l|o|e|i|ende|
8.481767668158573   v|l|o|e|i|+VPRS*|   v|l|o|e|o|_|
8.37277993506041    v|l|o|e|i|+VPRS*|   v|l|o|e|_|_|
8.35691886128588    v|l|o|e|i|+VPRS*|   v|l|o|e|ï|_|
8.324563677532955   v|l|o|e|i|+VPRS*|   v|l|o|e|in|_|
7.784302446215115   v|l|o|e|i|+VPRS*|   v|l|o|w|i|_|
7.765452034811237   v|l|o|e|i|+VPRS*|   v|l|o|ë|i|_|
11.072084554962432  VPST*+|v|l|o|e|i|+VPST*|    ge|v|l|o|e|i|_|
...

PhraseOut:
v|l|o|e|i|+VPRS*|   v|l|o|e|i|_|    1   28.9729
v|l|o|e|i|+VPRS*|   v|l|o|e|e|_|    2   25.1692
v|l|o|e|i|+VPRS*|   v|l|o|e|i|ende| 3   24.8715
v|l|o|e|i|+VPRS*|   v|l|o|e|o|_|    4   24.1119
v|l|o|e|i|+VPRS*|   v|l|o|e|_|_|    5   23.802
v|l|o|e|i|+VPRS*|   v|l|o|e|ï|_|    6   23.7569
v|l|o|e|i|+VPRS*|   v|l|o|e|in|_|   7   23.6649
v|l|o|e|i|+|VPRS*|  v|l|o|e|i|_|_|  8   22.332
v|l|o|e|i|+VPRS*|   v|l|o|w|i|_|    9   22.1287
v|l|o|e|i|+VPRS*|   v|l|o|ë|i|_|    10  22.0751

v|l|o|e|i|+VPRS*|   v|l|o|e|i|_|    1   28.9729
...
'''

from __future__ import print_function, division
import os
import sys
import codecs
import fnmatch
import re
from collections import defaultdict

def scoreResults(inDir, outDir, dec=2):
	posList = ['noun', 'verb']
	dir = os.listdir(inDir)
	# collect goldfiles in input data dir by part of speech
	goldFiles = defaultdict(list)
    for pos in posList:
    	goldFiles[pos] = fnmatch.filter(dir, '*'+pos+"_gold.txt")
    rrFiles = {}
    outFiles = {}
    for pos in posList:
    	rrFiles[pos] = {}
    	outFiles[pos] = {}
    # search recursively in output dir for relevant files
    for dirPath, dirNames, filenames in os.walk(outDir):
	    for filename in filenames:
	    	if filename.endswith("_reranked.txt"):
	    		strList = filename.split("_")
	    		lang, pos = "_".join(strList[:-2]), str(strList[-2:-1])
	    		rrFiles[pos][lang] = os.path.join(dirPath, filename)
	    	elif filename.endswith(".phraseOut"):
	    		strList = re.split(r'[_.]', filename)
	    		lang, pos = "_".join(strList[:-2]), str(strList[-2:-1])
	    		outFiles[pos][lang] = os.path.join(dirPath, filename)

    for pos in posList:
    	for goldFile in goldFiles[pos]:
        	language = "_".join(filename.split("_")[:-2])
            sys.stdout.write("Scoring "+language+" "+pos+"s\n")
            goldPath = os.path.join(inDir, goldFile)
            scoreFilename = os.path.join(outDir, language, language+"_"+pos+"_"+"_scores.txt")
            with codecs.open(scoreFilename, 'w', encoding="utf-8") as scoreFile:
	            if (file = rrFiles.get(pos).get(language)):
	            	formScore = 0
	            	totalForms = 0
	            	scoreFile.write(language+" "+pos+" "+" reranked:\n")
	           		with codecs.open(goldPath, 'r', encoding="utf-8") as goldFile:
		            	with codecs.open(file, 'r', encoding="utf-8") as rrFile:
		            		prevProb = 0
		            		# use these to see if whole paradigm correct
		            		# when read lemma doesnt match prevLemma,
		            		# if prevLemmaCnt == (formScore - prevScore), whole paradigm is right
		            		prevScore = 0
		            		prevLemma = ""
		            		prevLemmaCnt = 0
		            		for i in goldFile:
		            			i = i.split()
		            			j = rrFile.readline()
		            			j = re.sub('[|_]', '', j)
		            			# skip through the other nBest answers
			        			while (j[1] != i[0]) or (j[0] < prevProb):
			        				prevProb = float(j[0])
			        				j = rrFile.readline()
			            			j = re.sub('[|_]', '', j)
			            		prevProb = float(j[0])
			            		if (prevLemma != "") and (''.join(x for x in i if x.islower()) == prevLemma):

		            			prevLemma = ''.join(x for x in i if x.islower())
		        				totalForms += 1
		        				if j[1] == i[1]:
		        					formScore += 1
		        	scoreFile.write("\tForm Accuracy: "+ '%.'+dec+'f' % (100 * formScore/totalForms) +"%%\n")
		        if (file = outFiles.get(pos).get(language)):
	            	formScore = 0
	            	totalForms = 0
		        	scoreFile.write(language+" "+pos+" "+" predictions:\n")
	           		with codecs.open(goldPath, 'r', encoding="utf-8") as goldFile:
		            	with codecs.open(file, 'r', encoding="utf-8") as outFile:
		            		for i in goldFile:
		            			tried = 1
		            			i = i.split()
		            			j = outFile.readline()
		            			j = re.sub('[|_]', '', j)
	            				j = j.split()[:2]
			        			while (j[0] != i[0]) and (tried < nBest):
			        				tried += 1
			        				j = outFile.readline()
			            			j = re.sub('[|_]', '', j)
			        				j = j.split()[:2]
			        			if tried == nBest:
			        				sys.stderr.write("\tNo answer for slot: "+ i[0] +"\n")
			        				continue
			        			else:
			        				totalForms += 1
			        				if j[1] == i[1]:
			        					formScore += 1
		        	scoreFile.write("\tForm Accuracy: "+ '%.'+dec+'f' % (100 * formScore/totalForms) +"%%\n")
		        else:
		        	sys.stderr.write(language+" "+pos+" "+" has nothing to score!\n")


