#!/usr/bin/env python3
'''Do SVM prediction for a reranking problem.

This program functions in a way similar to the libsvm svm-predict (or liblinear
predict) program. Given the test data for a reranking problem (using SVMlight's
reranking format), this program reads a liblinear model that has been trained
on training data that represents a reranking problem but that had been
converted to SVM binary classification form. This allows us to skip the step of
converting the test data into SVM form, running liblinear's predict, and then
converting it back; since the liblinear model provides easily-readable weights
we can use those directly. Usage is the same as liblinear's predict, except
output is on stdout.

Changelog:
__author__ = Sean Erfurt
    Added support for utf-8 encoded filenames and characters.
    Added error handling for KeyError.
'''

from sys import argv, stderr, stdout
import codecs

__author__ = 'Aditya Bhargava'
__license__ = 'FreeBSD'
__version__ = '1.1.0'
__email__ = 'aditya@cs.toronto.edu'


with open(argv[2]) as win:
    win.readline() # solver_type
    win.readline() # nr_class
    firstlabel = int(win.readline().split()[1]) # label
    neg = False
    if firstlabel == -1:
        neg = True
    elif firstlabel == 1:
        neg = False  # AB: these considerations added in v1.1.0
    maxFeat = int(win.readline().split()[1]) # nr_feature
    #weights = []
    weights = {}
    win.readline() # bias
    win.readline() # w
    feat = 1
    for line in win:
        weights[feat] = float(line)
        feat += 1
        #weights.append(weight)

with codecs.open(codecs.encode(argv[1],'utf-8','replace'), 'r', encoding='utf-8') as inp:
    for line in inp:
        contents = line.split(' # ')
        featstr = contents[0].strip().split(' ')[2:]
        feats = {}
        for s in featstr:
            stuff = s.split(':')
            feats[int(stuff[0])] = float(stuff[1])

        score = 0
        for feat in feats:
            try:
                #score += weights[feat - 1] * feats[feat]
                score += weights[feat] * feats[feat]
            except IndexError:
                print(maxFeat, feat, file=stderr)
                if feat <= maxFeat:
                    print(maxFeat, feat, file=stderr)
                    exit(1)
            except KeyError:
                stderr.write("Weight not found for feature: "+str(feat)+'\n')

        if neg:
            score *= -1
        info = ''.join(c for c in contents[1].strip() if c not in
                       "[]',").replace('NALGN NULL', 'NALGN NONE').split(' ')
        stdout.buffer.write(bytes(str(score) +'\t'+ '\t'.join([s for s in info if s != 'NULL']) +'\n', 'utf-8'))