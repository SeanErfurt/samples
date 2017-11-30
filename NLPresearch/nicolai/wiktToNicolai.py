
# coding: utf-8

# Author: Sean Erfurt
#   with credit to: John Sylak-Glassman

# Requires: Python 2.7+
#           pandas installed on local environment

# Execute code:
# python wiktToNicolai.py InDir/ OutDir/ {default|max|inc}

# Directories must end in "/". Generates training, testing, gold and tagfiles
# for use with Nicolai's code.
# argv[3]=max to use maximal paradigm only,
#        =default or "" to use all lemmas
#        =inc (incomplete) to use all lemmas and find missing paradigm slots

# Train files are space separated characters, with input / output tab-separated
#   ex.     g e b e n + 1SIE*   g e b e

# Test files are in format:
#   ex.     l|e|s|e|n|+|1SIE*

# Missing paradigm slots are also in test file format

# Tag files contain 1 concatenated feature vector per line, no repeats
#   ex.     INDNPRS1SG*

# Gold files contain the input and correct output to DTL, one per line, tab separated:
#   ex.     atmen+1SIE*    atme

# TODO: Extend to any part of speech, and consolidate repeated code

#CHANGELOG:
# 8-12-2015 @Sean: added support for certain chars to be turned into '_'
#                   which is the null char for the Nicolai process.
#                  added 'inc', incomplete mode, which outputs the missing
#                   paradigm slots (based on full set observed in language)
#                   in testfile format to *_missing.txt, in addition
#                   to the default (non-maximal) processes.
#                  improved readability of feature vector tags.
# 8-14-2015 @Sean: code restructuring. Some languages have large taglists
#                   and sparse data, making the *_missing files very large.
#                   May have to consider filtering somehow.
# 8-21-2015 @Sean: allowing spaces made some inflections in Armenian, Russian,
#                   etc. contain both native-written and transliterated spellings,
#                   causing serious errors with the output. Added classifying
#                   step so that only one spelling is accepted.
#                  also made fix to choose one dialect per inflection, but still
#                   keeps auxilary words (using longest common subsequence).
#                  made fix to remove tricky emdashes from output.

from __future__ import print_function, division
import pandas as pd
import os
import re
import sys
import codecs
import string
from collections import defaultdict, OrderedDict

# LCS helper function from http://rosettacode.org/wiki/Longest_common_subsequence#Python
def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result

def wiktToNicolai(wiktionaryDataDirectory,outputDirectory,mode="default"):
    # constant sets
    category = ["Polarity","Information Structure","Mood","Part of Speech","Definiteness","Switch-Reference",
        "Politeness","Possession","Interrogativity","Aktionsart","Tense","Case","Comparison","Valency","Gender",
        "Person","Voice","Animacy","Number","Finiteness","Aspect","Evidentiality","Deixis"] # + cell_value=inflection,page_url=baseform,language=FullLength
    invalidChars = set(string.digits + re.sub(r'[]{}"\'()/,;\-_[]',"", string.punctuation) + re.sub(' ', '', string.whitespace))
    excludeIfInflEquals = set([u"singular",u"Singular",u"plural",u"Plural",u"none",u"Present",u"Past",u"Future",u"Masculine",u"Feminine",u"Neuter",u"animate",
        u"inanimate",u"acc.",u"first",u"second",u"third",u"all",u"eg",u"sg",u"pl",u"Present",u"Imperfect",u"Dependent",u"Perfective",u"Perfect",u"Continuous",
        u"Simple",u"Imperfective",u"Nominative",u"Vocative",u"Genitive",u"Dative",u"Passive",u"Causative",u"Potential",u"Volitional",u"Negative",u"Formal",
        u"Conjunctive",u"Determiners",u"imperative",u"unchanged",u"*rare",u"Oblique",u"Subject",u"1st",u"2nd",u"3rd",u"Aorist",u"Imperative",u"Pluperfect",
        u"Number",u"Person",u"—3",u"*"])

    mode = mode.lower()
    # for backwards-compatibility
    if mode == "" or mode == "false":
        mode = "default"
    elif mode == "true":
        mode = "max"

    wiktionaryDataDirectoryFileList = os.listdir(wiktionaryDataDirectory)           # Creates a list of the files in that directory.
    for filename in wiktionaryDataDirectoryFileList:                                # Loop through all the input files
        if filename.endswith("_table.csv"):                                         # Find non-conflicts files with data
            language = "_".join(filename.replace(" ", "_").split("_")[:-1])         # Discover the language name from the file name.
            sys.stderr.write(language)
            dataPath = os.path.join(wiktionaryDataDirectory, filename)              # Create a full path to the data file.
            wD = pd.io.parsers.read_csv(dataPath,dtype=unicode,encoding="utf-8")    # Load each CSV data file as a pandas data frame with data encoded as utf-8.
            # open up tag files
            nTagFile = codecs.open(os.path.join(outputDirectory, language+"_noun_tags.txt"), 'w', encoding='utf-8')
            vTagFile = codecs.open(os.path.join(outputDirectory, language+"_verb_tags.txt"), 'w', encoding='utf-8')
            # set up data structures
            nounTags = defaultdict(set)
            verbTags = defaultdict(set)
            # some duplicates observed, currently keeping in case counts are useful #
            nounInfl = defaultdict(list)
            verbInfl = defaultdict(list)
            for i in range(len(wD.page_url)):                       # For every inflected form in the data file,
                # need to filter out null values and those with bad chars
                if (pd.isnull(wD.page_url[i]) == False and pd.isnull(wD.cell_value[i]) == False and wD.cell_value[i] not in excludeIfInflEquals and
                    not any(char in invalidChars for char in wD.page_url[i]) and not any(char in invalidChars for char in wD.cell_value[i])):
                    lemma = wD.page_url[i]                          # get the lemma name from the page_url column at the current index
                    # if contains transliterated and unicode words, separated by any separator, pick unicode
                    ls = re.split(r'[]{}"()/,;\-_— []', lemma)
                    if len(ls) != 1:
                        counts = OrderedDict()
                        ascii_l = ""
                        uni_l = ""
                        # take ascii counts for calculating transliteration probability
                        for word in ls:
                            for c in word:
                                if ord(c) < 128:
                                    counts[word] = counts.get(word, 0) + 1
                                else:
                                    counts[word] = counts.get(word, 0) - 1
                        probs = OrderedDict()
                        for k,v in counts.items():
                            probs[k] = v/len(k)
                        # collect words with similar probabilities #
                        for k,v in probs.items():
                            if v >= -0.5:
                                if ascii_l:
                                    # dont append if too similar (likely a different dialect)
                                    if (len(lcs(ascii_l, k))/len(k)) < 0.5:
                                        ascii_l += "_"+ k
                                else:
                                    ascii_l = k
                            else:
                                if uni_l:
                                    # dont append if too similar (likely a different dialect)
                                    if (len(lcs(uni_l, k))/len(k)) < 0.5:
                                        uni_l += "_"+ k
                                else:
                                    uni_l = k
                        if uni_l != "":
                            lemma = uni_l # prefer unicode #
                        else:
                            lemma = ascii_l
                    else:
                        lemma = re.sub(r'[]{}"()[]','',lemma)           # remove any useless delimiters
                        lemma = re.sub(r'[-— ]','_',lemma)               #replace hyphens, emdashes, spaces with underscores #
                        if re.search(r'[/,;]', lemma):               #toss if it has any of these characters
                            continue
                    #print("After: "+lemma.encode("utf-8"))
                    #toss lemma if it is empty or emdash
                    if (lemma == "") or (lemma == "_") or (lemma == u"\u2014"):
                        continue
                    pos = ""
                    fullFeatureVector = ""                          # initialize a string that will hold the feature vector.
                    for dimension in category:                      # then, for each column that has the name of a dimension of meaning,
                        if pd.isnull(wD[dimension][i]) == False:
                            feature = wD[dimension][i]              # store the value of that column in the current row as rawFeature
                            if dimension == "Part of Speech":
                                pos = feature
                            #ignore punctuation (could be an alternate value or formatting error)
                            feature = re.sub(r'[] \-—_{}"\'()/,;\+\*[]','',feature)
                            fullFeatureVector += feature.capitalize()
                    # group tags by part of speech and lemma
                    if pos == "V":
                        exists = False
                        for s in verbTags.values():
                            if fullFeatureVector in s:
                                exists = True
                                break
                        if not exists:
                            vTagFile.write(fullFeatureVector + "*\n")
                        verbTags[lemma].add(fullFeatureVector)
                    elif pos == "N":
                        exists = False
                        for s in nounTags.values():
                            if fullFeatureVector in s:
                                exists = True
                                break
                        if not exists:
                            nTagFile.write(fullFeatureVector + "*\n")
                        nounTags[lemma].add(fullFeatureVector)
                    # toss if not noun or verb, likely insufficient data #
                    else:
                        continue

                    infl = wD.cell_value[i]                         # get the inflected form from the cell_value column at the current index
                    # if contains transliterated and unicode words, separated by any separator, pick unicode
                    #print("Before: "+infl.encode("utf-8"))
                    infls = re.split(r'[]{}"()/,;\-_— []', infl)
                    #print("Split: "+str(infls).encode("utf-8"))
                    if len(infls) != 1:
                        counts = OrderedDict()
                        ascii_i = ""
                        uni_i = ""
                        # take counts for calculating transliteration probability
                        for word in infls:
                            for c in word:
                                if ord(c) < 128:
                                    counts[word] = counts.get(word, 0) + 1
                                else:
                                    counts[word] = counts.get(word, 0) - 1
                        probs = OrderedDict()
                        for k,v in counts.items():
                            probs[k] = v/len(k)
                        #print(str(probs))
                        # collect words with similar probabilities #
                        for k,v in probs.items():
                            if v >= -0.5:
                                if ascii_i:
                                    # dont append if too similar (likely a different dialect)
                                    if (len(lcs(ascii_i, k))/len(k)) < 0.5:
                                        ascii_i += "_"+ k
                                else:
                                    ascii_i = k
                            else:
                                if uni_i:
                                    # dont append if too similar (likely a different dialect)
                                    if (len(lcs(uni_i, k))/len(k)) < 0.5:
                                        uni_i += "_"+ k
                                else:
                                    uni_i = k
                        if uni_i != "":
                            infl = uni_i # prefer unicode #
                        else:
                            infl = ascii_i
                    else:
                        infl = re.sub(r'[]{}"()[]','',infl)        # remove any useless delimiters
                        infl = re.sub(r'[-— ]','_',infl)               #replace hyphens, emdashes, spaces with underscores (could be an auxilary) #
                        if re.search(r'[/,;]', infl):           #toss if it has any of these characters
                            continue
                    #print("After: "+infl.encode("utf-8"))
                    #toss inflection if it is empty or emdash
                    if (infl == "") or (infl == "_") or (infl == u"\u2014"):
                        continue
                    #create output line
                    output = ""
                    #if first letters are different, assume circumfixing (always assume suffixing) #
                    if (infl[0] != lemma[0]):
                        output = fullFeatureVector + "* + "
                    output += " ".join(list(lemma)) + " + " + fullFeatureVector + "*\t" + " ".join(list(infl)) + "\n"
                    #group inflections by part of speech and lemma
                    if pos == "V":
                        verbInfl[lemma].append(output)
                    else:
                        nounInfl[lemma].append(output)
                    '''
                    # some punctuation actually signifies different inflections for same pos tag (dialects)
                    inflections = re.split(r'[/,;]', infl) # what to do considering 'multiple encodings' vs. 'multiple dialects'?
                    for k in inflections:
                        if k != "":
                            #create output line
                            output = ""
                            #if first letters are different, assume circumfixing
                            if (k[0] != lemma[0]):
                                output = fullFeatureVector + "* + "
                            output += " ".join(list(lemma)) + " + " + fullFeatureVector + "*\t" + " ".join(list(k)) + "\n"
                            #group inflections by part of speech and lemma
                            if pos == "V":
                                verbInfl[lemma].append(output)
                            else:
                                nounInfl[lemma].append(output)
                    '''
                if i % 1000 == 0:
                    sys.stderr.write(".")
            nTagFile.close()
            vTagFile.close()
            print("")
            # create train and test sets

            #doing verbs
            lemmas = []
            tags = []
            if mode == "max":
                # paradigms will hold sets of lemmas keyed by their common tagSet (i.e. paradigm)
                paradigms = defaultdict(set)
                for k, v in verbTags.items():
                    paradigms[frozenset(v)].add(k)
                for k, v in paradigms.items():
                    if len(v) > len(lemmas):
                        tags = list(k)
                        lemmas = list(v)
            else:
                with codecs.open(os.path.join(outputDirectory, language+"_verb_tags.txt"), 'r', encoding='utf-8') as vTagFile:
                    tags = [line.rstrip('*\n') for line in vTagFile]
                lemmas = verbTags.keys()
            #print(lemmas)
            verbLen = len(lemmas)
            if verbLen < 10:
                print("Insufficient data for: "+language+" verbs")
                os.remove(os.path.join(outputDirectory, language+"_verb_tags.txt"))
            elif verbLen >= 2000:
                train = lemmas[:-200]
                train_500 = lemmas[:500]    # Create learning curve training sets
                train_100 = lemmas[:100]
                train_50 = lemmas[:50]
                train_10 = lemmas[:10]
                test = lemmas[-200:]         #different format, handle separately
                print(language+" verb lemmas for training: " + str(len(train)))
                print(language+" verb lemmas for testing: " + str(len(test)))
                dataToWrite = [train,train_500,train_100,train_50,train_10]
                dataToWriteNames = ["train","train_500","train_100","train_50","train_10"]
                msngCnt = 0
                unseenfilename = os.path.join(outputDirectory, language+"_verb_missing.txt")
                unseenfile = codecs.open(unseenfilename, 'wb', encoding='utf-8')
                for k in dataToWrite:
                    newfilename = os.path.join(outputDirectory, language+"_verb_"+dataToWriteNames[dataToWrite.index(k)]+".txt")
                    with codecs.open(newfilename, 'wb', encoding='utf-8') as newfile:
                        for l in k:
                            if (mode == "inc"):
                                for t in tags:
                                    if t not in verbTags[l]:
                                        msngCnt += 1
                                        line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                        unseenfile.write(line)
                            for i in verbInfl[l]:
                                newfile.write(i)
                testfilename = os.path.join(outputDirectory, language+"_verb_test.txt")
                goldfilename = os.path.join(outputDirectory, language+"_verb_gold.txt")
                with codecs.open(testfilename, 'wb', encoding='utf-8') as newfile:
                    goldfile = codecs.open(goldfilename, 'wb', encoding='utf-8')
                    for l in test:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in verbTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in verbInfl[l]:
                            question = i.split("\t")[0]
                            question = re.sub(r' ', "|", question)       #reformats for test file
                            answer = re.sub(r' ', "", i)
                            newfile.write(question + "\n")
                            goldfile.write(answer)
                    goldfile.close()
                unseenfile.close()
                if msngCnt == 0:
                    os.remove(os.path.join(outputDirectory, language+"_verb_missing.txt"))
                else:
                    print("Missing inflected "+ language +" verb forms: "+ str(msngCnt))
            else:
                testLength = verbLen//10    # This causes a test list of no more than 10%
                # of the data, and sometimes slighlty less since 1529/10 = 152.9 => 152 as an integer here
                train = lemmas[:-testLength]
                test = lemmas[-testLength:]
                print(language+" verb lemmas for training: " + str(len(train)))
                print(language+" verb lemmas for testing: " + str(len(test)))
                trainfilename = os.path.join(outputDirectory, language+"_verb_train.txt")
                msngCnt = 0
                unseenfilename = os.path.join(outputDirectory, language+"_verb_missing.txt")
                unseenfile = codecs.open(unseenfilename, 'wb', encoding='utf-8')
                with codecs.open(trainfilename, 'wb', encoding='utf-8') as newfile:
                    for l in train:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in verbTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in verbInfl[l]:
                            newfile.write(i)
                testfilename = os.path.join(outputDirectory, language+"_verb_test.txt")
                goldfilename = os.path.join(outputDirectory, language+"_verb_gold.txt")
                with codecs.open(testfilename, 'wb', encoding='utf-8') as newfile:
                    goldfile = codecs.open(goldfilename, 'wb', encoding='utf-8')
                    for l in test:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in verbTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in verbInfl[l]:
                            question = i.split("\t")[0]
                            question = re.sub(r' ', "|", question)       #reformats for test file
                            answer = re.sub(r' ', "", i)
                            newfile.write(question + "\n")
                            goldfile.write(answer)
                    goldfile.close()
                unseenfile.close()
                if msngCnt == 0:
                    os.remove(os.path.join(outputDirectory, language+"_verb_missing.txt"))
                else:
                    print("Missing inflected "+ language +" verb forms: "+ str(msngCnt))
            #end doing verbs

            #doing nouns
            lemmas = []
            tags = []
            if mode == "max":
                # paradigms will hold sets of lemmas keyed by their common tagSet (i.e. paradigm)
                paradigms = defaultdict(set)
                for k, v in nounTags.items():
                    paradigms[frozenset(v)].add(k)
                for k, v in paradigms.items():
                    if len(v) > len(lemmas):
                        tags = list(k)
                        lemmas = list(v)
            else:
                with codecs.open(os.path.join(outputDirectory, language+"_noun_tags.txt"), 'r', encoding='utf-8') as nTagFile:
                    tags = [line.rstrip('*\n') for line in nTagFile]
                lemmas = nounTags.keys()

            nounLen = len(lemmas)
            if nounLen < 10:
                print("Insufficient data for: "+language+" nouns")
                os.remove(os.path.join(outputDirectory, language+"_noun_tags.txt"))
            elif nounLen >= 2000:
                train = lemmas[:-200]
                train_500 = lemmas[:500]    # Create learning curve training sets
                train_100 = lemmas[:100]
                train_50 = lemmas[:50]
                train_10 = lemmas[:10]
                test = lemmas[-200:]         #different format, handle separately
                print(language+" noun lemmas for training: " + str(len(train)))
                print(language+" noun lemmas for testing: " + str(len(test)))
                dataToWrite = [train,train_500,train_100,train_50,train_10]
                dataToWriteNames = ["train","train_500","train_100","train_50","train_10"]
                msngCnt = 0
                unseenfilename = os.path.join(outputDirectory, language+"_noun_missing.txt")
                unseenfile = codecs.open(unseenfilename, 'wb', encoding='utf-8')
                for k in dataToWrite:
                    newfilename = os.path.join(outputDirectory,language+"_noun_"+dataToWriteNames[dataToWrite.index(k)]+".txt")
                    with codecs.open(newfilename, 'wb', encoding='utf-8') as newfile:
                        for l in k:
                            if (mode == "inc"):
                                for t in tags:
                                    if t not in nounTags[l]:
                                        msngCnt += 1
                                        line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                        unseenfile.write(line)
                            for i in nounInfl[l]:
                                newfile.write(i)
                testfilename = os.path.join(outputDirectory,language+"_noun_test.txt")
                goldfilename = os.path.join(outputDirectory, language+"_noun_gold.txt")
                with codecs.open(testfilename, 'wb', encoding='utf-8') as newfile:
                    goldfile = codecs.open(goldfilename, 'wb', encoding='utf-8')
                    for l in test:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in nounTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in nounInfl[l]:
                            question = i.split("\t")[0]
                            question = re.sub(r' ', "|", question)       #reformats for test file
                            answer = re.sub(r' ', "", i)
                            newfile.write(question + "\n")
                            goldfile.write(answer)
                    goldfile.close()
                unseenfile.close()
                if msngCnt == 0:
                    os.remove(os.path.join(outputDirectory, language+"_noun_missing.txt"))
                else:
                    print("Missing inflected "+ language +" noun forms: "+ str(msngCnt))
            else:
                testLength = nounLen//10    # This causes a test list of no more than 10%
                # of the data, and sometimes slighlty less since 1529/10 = 152.9 => 152 as an integer here
                train = lemmas[:-testLength]
                test = lemmas[-testLength:]
                print(language+" noun lemmas for training: " + str(len(train)))
                print(language+" noun lemmas for testing: " + str(len(test)))
                trainfilename = os.path.join(outputDirectory, language+"_noun_train.txt")
                msngCnt = 0
                unseenfilename = os.path.join(outputDirectory, language+"_noun_missing.txt")
                unseenfile = codecs.open(unseenfilename, 'wb', encoding='utf-8')
                with codecs.open(trainfilename, 'wb', encoding='utf-8') as newfile:
                    for l in train:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in nounTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in nounInfl[l]:
                            newfile.write(i)
                testfilename = os.path.join(outputDirectory, language+"_noun_test.txt")
                goldfilename = os.path.join(outputDirectory, language+"_noun_gold.txt")
                with codecs.open(testfilename, 'wb', encoding='utf-8') as newfile:
                    goldfile = codecs.open(goldfilename, 'wb', encoding='utf-8')
                    for l in test:
                        if (mode == "inc"):
                            for t in tags:
                                if t not in nounTags[l]:
                                    msngCnt += 1
                                    line = t +"*|+|"+ "|".join(list(l)) +"|+|"+ t +"*\n"
                                    unseenfile.write(line)
                        for i in nounInfl[l]:
                            question = i.split("\t")[0]
                            question = re.sub(r' ', "|", question)       #reformats for test file
                            answer = re.sub(r' ', "", i)
                            newfile.write(question + "\n")
                            goldfile.write(answer)
                    goldfile.close()
                unseenfile.close()
                if msngCnt == 0:
                    os.remove(os.path.join(outputDirectory, language+"_noun_missing.txt"))
                else:
                    print("Missing inflected "+ language +" noun forms: "+ str(msngCnt))
            #end doing nouns

wiktionaryDataDirectory = sys.argv[1]  # Where the Wiktionary data files are. This must end with "/".
outputDirectory = sys.argv[2]     # Where the produced files should be placed. This must end with "/".
try:
    mode = sys.argv[3]
except IndexError:
    mode = ""
wiktToNicolai(wiktionaryDataDirectory,outputDirectory,mode)

