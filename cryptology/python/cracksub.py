import json
import string
from collections import Counter, OrderedDict, defaultdict
from pprint import pprint
import random

# set of possible keys (assumption)
alphabet = string.ascii_lowercase
# order of most frequent english characters
standard_mfcs = "etaoinshrdlucmfwypvbgkjqxz"
# common short words to look for when validating possible decryptions
words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 'her',
         'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new',
         'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say',
         'she', 'too', 'use']


def cracksub(ciphertext, mode="frequency", num_trials=1000000, mapping={}, ignore_ws=False):
    """
    Attempt to crack a substitution cipher.
    :param ciphertext: the encoded message as a string
    :param mode: whether to use standard English character frequencies (default) or random mapping
    :param num_trials: number of trials to run if using random mappings (default is 1000000)
    :param mapping: optional dictionary with cipher => plain character mappings
    :param ignore_ws: whether to keep original whitespace in message (default) or ignore it
    :return: if frequency mode, the plaintext generated. Else, potential word mappings to use.
    """
    # remove whitespace for calculating relative frequencies
    no_ws_text = ''.join(ciphertext.split())
    if ignore_ws:
        ciphertext = no_ws_text
    mfcs = getMFCs(no_ws_text)
    print("Most Frequent cipher characters:")
    pprint(list(mfcs.keys()), compact=True)
    # Find un-mapped letters
    unused_in = [x for x in mfcs.keys() if x not in mapping.keys()]
    unused_out = [x for x in standard_mfcs if x not in mapping.values()]
    print("Cipher Text: " + ciphertext)
    # Frequency-based mapping
    if mode == "frequency":
        # assign un-mapped letters in order
        for i, c in enumerate(unused_in):
            mapping[c] = unused_out[i]
        plaintext = ciphertext.translate(str.maketrans(mapping))
        print("Output Text: " + plaintext)
        return plaintext
    # Brute force solution with random mappings and filtering for common short words in output
    else:
        found = defaultdict(list)
        for i in range(0, num_trials):
            random_out = random.sample(list(unused_out), k=len(unused_out))
            # assign un-mapped letters using random permutation of unassigned output letters
            for i, c in enumerate(unused_in):
                mapping[c] = random_out[i]
            plaintext = ciphertext.translate(str.maketrans(mapping))
            # search plaintext for valid words
            c, p = findWord(ciphertext, plaintext)
            if c:
                found[c].append(p)
                words.remove(p)  # avoid getting lots of junk permutations on one "hit"
        return found

def encodeSub(plaintext, mapping={}):
    """
    Use a substitution cipher to encode a message.
    :param plaintext: the message to encode
    :param mapping: optional dictionary to use when encoding
    :return [encoded message, {mapping}]
    """
    no_ws_text = ''.join(plaintext.split())
    # if there is no mapping or if the mapping is incomplete, generate a new one randomly
    if not(mapping and len(mapping.keys()) == len(alphabet)):
        random_out = random.sample(list(alphabet), k=len(alphabet))
        for i, c in enumerate(alphabet):
            mapping[c] = random_out[i]
    ciphertext = no_ws_text.translate(str.maketrans(mapping))
    return ciphertext, mapping


def getMFCs(text):
    """
    Get most frequent characters in text, and their relative frequency values
    :param text: the string
    :return: an Ordered Dict, char => relFreq, most frequent first (descending)
    """
    relFreq = {}
    chars = len(text)
    cnt = Counter(text)
    for i in alphabet:
        relFreq[i] = (cnt[i] / chars)
    # order by frequency descending
    mfcs = OrderedDict(sorted(relFreq.items(), key=lambda t: t[1], reverse=True))
    return mfcs


def findWord(ciphertext, plaintext):
    """
    Search plaintext for common short words. Return the first one and its ciphertext counterpart.
    :param ciphertext: the original message
    :param plaintext: the decoded message
    :return the mapping for the found word as a list [cipher,plain], or [None, None] if no words found
    """
    for w in words:
        index = plaintext.find(w)
        if index != -1:
            print("Output Text: " + plaintext)
            cipher = ciphertext[index:index + len(w)]
            return [cipher, w]
    return [None, None]


if __name__ == "__main__":
    message = 'The quick brown fox jumps over the lazy dog'
    try:
        with open("subAnswer.txt", mode="r") as answers:
            mapping_answer = json.loads(answers)
    except:
        with open("subAnswer.txt",mode="w") as answers:
            cipher, mapping_answer = encodeSub(message)
            answers.write(json.dumps(mapping_answer))
    m = {}
    found = cracksub(cipher, mapping=m, mode=1)
    pprint(found)
    # use found dictionary to make educated guesses in m, then iterate until a message appears
