# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>
import numpy as np
import random

'''
Sean's LLM: a toy Log-linear Model for learning the basics of logistic regression
    @see https://en.wikipedia.org/wiki/Logistic_regression#As_a_.22log-linear.22_model
'''

num_classes = 2
num_features = 10
training_data = np.asarray([1, 1, 0, 0, 1, 1, 1, 1, 0])
features = np.zeros((len(training_data), num_classes, num_features))

# Un-comment a feature generation scheme #########################################
'''
# random distribution
features = np.round(np.random.rand(len(training_data), num_classes, num_features))
'''
'''
# all features for each element get set to training_data value
for i,d in enumerate(training_data):
    features[i] = np.vstack((np.full(num_features, 1 - d), np.full(num_features, d)))
'''
# '''
# give one class of elements one set of features, and the other a different set.
# Should make classifying easy.
firstFeats = np.round(np.random.rand(num_features))
secondFeats = np.round(np.random.rand(num_features))
for i, d in enumerate(training_data):
    if d == 0:
        features[i] = np.vstack((firstFeats, secondFeats))
    else:
        features[i] = np.vstack((secondFeats, firstFeats))
# '''
# END Feature Generation Schemes ################################################
'''
NOTES
exp(x) > 0, for any real number x 
lim x -> -\infty exp(x) = 0

Calculating probability?
We have a set X = {0, 1, 2}
1) We assign a score to each element, e.g., score(2)
2) We take the exponential (guaranteed to be non-negative)
3) We renormalize

Z = exp(score(0)) + exp(score(1)) + exp(score(2))
p(1) = exp(score(1)) / Z

score() = dot(theta, features)
dot(theta, features) = \sum_i theta_i * features_i 
dot([2, 3, 5] , [-4, 3, 9]) = 46

Q: How do you choose theta?
A: Maximum liklihood estimate (MLE) 

MLE means choose the theta that maximizes the probability of the training data.

Optimization problem!
Algorithm (Gradient Descent):

for k in range(ITERATIONS):
    theta <- theta_k - alpha * p(theta_k) )
    
But be aware of over-fitting the model to the training data!
'''


def p(theta):
    """
    Computes the log-likelihood of the training data
    """
    ll = 0.0
    for i, gold in enumerate(training_data):
        # compute partition function
        Z = 0.0
        for elem in range(num_classes):
            Z += np.exp(np.dot(theta, features[i, elem]))
        ll += np.log(np.exp(np.dot(theta, features[i, gold])) / Z)
    return np.exp(ll)


def main(gold_data=training_data, feats=features, num_iter=10000, start="zero", step=0.2):
    # TODO: accept training data from an external file, and pass it to p() where appropriate
    # TODO: derive number of classes and features if training data is provided
    # TODO: if training data is provided, segment out some test data and evaluate model at end
    # TODO: expose option for feature generation scheme, and precision for maximal probability
    print("Features:")
    print(feats)
    arg_max = []
    pval = 0
    # set initial weights
    if start == "rand":
        theta = np.random.rand(num_features)
    elif isinstance(start, (np.ndarray, list)):
        theta = start
    else:
        theta = np.zeros(num_features)

    # get max theta and log-likelihood
    for k in range(1, num_iter + 1):
        # introduce random variation
        theta = [x - (step * (random.random() - 0.5)) for x in theta]
        value = p(theta)
        if arg_max:
            pval = max(value, pval)
            # if new value is larger, replace arg_max
            if pval == value:
                arg_max = theta
        # base case
        else:
            arg_max, pval = theta, value
        if k % 100 == 0:
            print("[" + str(k) + "]" + " Weights: " + str(arg_max) + " Log-Likelihood: " + str(pval) + '\n')
        if round(pval, 3) >= 1.0:
            print("Log-likelihood maximized with weights:\n" + str(arg_max))
            break
    return arg_max


if __name__ == '__main__':
    # Anecdotally, initializing weights randomly leads to faster and more consistent results.
    # This is probably because it helps keep the gradient descent from getting stuck in a local max
    main(start="rand")
