import json
import string
from collections import Counter, OrderedDict, defaultdict
from pprint import pprint
import random
import requests

# set of possible keys (assumption)
alphabet = string.ascii_lowercase
# order of most frequent english characters
standard_mfcs = "etaoinshrdlucmfwypvbgkjqxz"


def loadWords(word_list):
    '''
    Load in the selected word list for searching in plaintext.
    :param word_list: string matching one of: { (s)hort | (m)edium | (l)ong }
    :return: list of strings
    '''
    if word_list.lower().startswith("s"):
        # short list: most common 3-letter words
        words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 'her',
                 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new',
                 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say',
                 'she', 'too', 'use']
    elif word_list.lower().startswith("m"):
        # medium-size list: 3000 most common words
        with open("words.txt", mode="r") as w:
            words = list(json.load(w))
    else:
        # large list: 466,000 English words
        try:
            with open("wordList.txt", mode="r") as w:
                words = list(json.load(w))
        except IOError:
            with open("wordList.txt", mode="w") as w:
                r = requests.get('http://raw.githubusercontent.com/dwyl/english-words/master/words_dictionary.json')
                words = list(dict(r.json()).keys())
                w.write(json.dumps(words))
    return words


def crackSub(ciphertext, mode="frequency", num_trials=100000, mapping=None, ignore_ws=False, word_list="short"):
    """
    Attempt to crack a substitution cipher.
    :param ciphertext: the encoded message as a string
    :param mode: whether to use standard English character frequencies (default) or random mapping
    :param num_trials: number of trials to run if using random mappings (default is 1000000)
    :param mapping: optional dictionary with cipher => plain character mappings
    :param ignore_ws: whether to keep original whitespace in message (default) or ignore it
    :param word_list: the list of words to search for in output { (s)hort | (m)edium | (l)ong }
    :return: if frequency mode, the plaintext generated. Else, potential word mappings to use.
    """
    # TODO add support for user-given alphabets (both in and out)
    if mapping is None:
        mapping = {}
    ciphertext = ciphertext.lower()
    # remove whitespace for calculating most frequent characters
    no_ws_text = ''.join(ciphertext.split())
    if ignore_ws:
        ciphertext = no_ws_text
    mfcs = [x[0] for x in Counter(no_ws_text).most_common()]
    print("Most Frequent cipher characters:")
    pprint(mfcs, compact=True)
    # Find un-mapped letters
    unused_in = [x for x in mfcs if x not in mapping.keys()]
    unused_out = [x for x in standard_mfcs if x not in mapping.values()]
    assert len(mfcs) == len(standard_mfcs), "input alphabet is not the same size as output alphabet"
    assert len(unused_in) == len(unused_out), "given mapping is not one-to-one"

    # Frequency-based mapping
    if mode.lower().startswith("f"):
        # assign un-mapped letters in order
        for i, c in enumerate(unused_in):
            mapping[c] = unused_out[i]
        plaintext = ciphertext.translate(str.maketrans(mapping))
        print("Cipher Text: " + ciphertext)
        print("Output Text: " + plaintext)
        return plaintext, mapping
    # Brute force solution with random mappings and filtering for common english words in output
    else:
        # Load words to search for
        words = loadWords(word_list)
        # accumulate words found, keyed by start index
        foundWords = defaultdict(list)
        for n in range(0, num_trials):
            random_out = random.sample(list(unused_out), k=len(unused_out))
            # assign un-mapped letters using random permutation of unassigned output letters
            for i, c in enumerate(unused_in):
                mapping[c] = random_out[i]
            plaintext = ciphertext.translate(str.maketrans(mapping))
            # search plaintext for valid words
            for i, w in enumerate(words):
                start = plaintext.find(w)
                if start != -1:
                    end = start + len(w)
                    print("Cipher Text:", ciphertext[0:start], ciphertext[start:end], ciphertext[end:])
                    print("Output Text:", plaintext[0:start], plaintext[start:end], plaintext[end:], "\n")
                    words.remove(w)  # avoid getting lots of repeated hits
                    foundWords[start].append(w)
        return foundWords


def encodeSub(plaintext, mapping=None):
    """
    Use a substitution cipher to encode a message.
    :param plaintext: the message to encode
    :param mapping: optional dictionary to use when encoding
    :return [encoded message, {mapping}]
    """
    if mapping is None:
        mapping = {}
    no_ws_text = ''.join(plaintext.split())
    # if there is no mapping or if the mapping is incomplete, generate a new one randomly
    if not (mapping and len(mapping.keys()) == len(alphabet)):
        random_out = random.sample(list(alphabet), k=len(alphabet))
        for i, c in enumerate(alphabet):
            mapping[c] = random_out[i]
    ciphertext = no_ws_text.translate(str.maketrans(mapping))
    return ciphertext, mapping


def printFW(found):
    '''
    Pretty-print the found words dictionary in order of index.
    :param found: dict
    '''
    for k, v in sorted(found.items(), key=lambda t:t[0]):
        print(k, end='\t')
        pprint(v)


if __name__ == "__main__":
    message = 'The quick brown fox jumps over the lazy dog'
    try:
        with open("subAnswer.txt", mode="r") as answers:
            mapping_answer = json.load(answers)
            cipher, _ = encodeSub(message, mapping_answer)
    except:
        with open("subAnswer.txt", mode="w") as answers:
            cipher, mapping_answer = encodeSub(message)
            answers.write(json.dumps(mapping_answer))

    plain, m = crackSub(cipher, mode="f") # get frequency mapping
    found = crackSub(cipher, mapping=m, mode="random", num_trials=1, word_list="m") # find words using freq map
    if found:
        printFW(found)

    # TODO Automate the word-finding/map-building to decode an arbitrary ciphertext
    # Top-level iter: found = crackSub(cipher, mapping=m, mode="random", num_trials=50, wordList="m")
    # # use found tree to make educated guesses in mapping, then iterate until a message appears
    # While message contains non-words (run crackSub in freq mode for output), run some trials and collect options
    # select word combinations that do not overlap from found options
    # e.g. message_i = 0,j=0, select found[m_i][j], assign map according to each char in found[m_i][j]
    # then set message_i = m_i + len(found[m_i][j] and j=0 and select found[m_i][j] again, but
    # if new found[m_i][j] has a conflicting assignment (in- or out-char is not in set(unused_in) or set(u_out), then
    # remove any intermediate assignments from invalid words & try the next found[m_i][j++] until it does not conflict
    # If we run out of words to try before we reach the end of the message, save max(m_i) & mapping & print spaced output.
    # Then message_i = 0 again and try the next found[0][j++]. Repeat until found[0] has all been tried.
    # Whichever word combination used the most letters will be output, and that char mapping is used for next trials.
    # ISSUE: this seems like recursion, but favors short words & starting words heavily. could get stuck on a bad start word.
    # is there a better Data Structure for this? randomly choose only some of the mapping to use?
    # Start off using smallest word list, then use more inclusive ones "later"? how to define "later"?
