import string
from collections import Counter, defaultdict, OrderedDict
from pprint import pprint
import random
import json
from nltk.corpus import stopwords, words

# set of possible keys (assumption)
alphabet = string.ascii_lowercase
# order of most frequent english characters
standard_mfcs = "etaoinshrdlucmfwypvbgkjqxz"


def loadWords(word_list):
    '''
    Load in the selected word list for searching in plaintext.
    :param word_list: int representing relatively-sized lists (1 == stop-words)
    :return: list of strings
    '''
    if word_list == 0:
        # short list: most common 3-letter words
        # @see: http://practicalcryptography.com/ciphers/simple-substitution-cipher/
        wordList = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 'her',
                 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new',
                 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say',
                 'she', 'too', 'use']
    elif word_list == 1:
        # stop-word list: from NLTK
        # @see http://www.nltk.org/book/ch02.html#code-unusual
        endings = set(['s', 't', 'd', 'm', 'o', 'y']) # exclude, count as stop-words but aren't words
        wordList = [w for w in stopwords.words('english') if w not in endings]
    elif word_list == 2:
        # medium-size list: 1949 most common words
        # @see http://preshing.com/20110811/xkcd-password-generator/
        with open("xkcdWords.txt", mode="r") as w:
            wordList = list(json.load(w))
    elif word_list == 3:
        # large list: 3000 most common words
        # @see https://www.ef.edu/english-resources/english-vocabulary/top-3000-words/
        with open("3kWords.txt", mode="r") as w:
            wordList = list(w)
    else:
        # largest list: NLTK Wordlist Corpora
        # @see http://www.nltk.org/book/ch02.html#code-unusual
        wordList = words.words()
    return wordList


def crackSub(ciphertext, mode="frequency", num_trials=100000, mapping=None, ignore_ws=False, word_list=0, silent=True):
    """
    Attempt to crack a substitution cipher.
    :param ciphertext: the encoded message as a string
    :param mode: whether to use standard English character frequencies (default) or random mapping
    :param num_trials: number of trials to run if using random mappings (default is 1000000)
    :param mapping: optional dictionary with cipher => plain character mappings
    :param ignore_ws: whether to keep original whitespace in message (default) or ignore it
    :param word_list: the list of words to search for in output { (s)hort | (m)edium | (l)ong }
    :param silent: if True (default), suppress output to stdout
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
    if not silent:
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
        if not silent:
            print("Cipher Text: " + ciphertext)
            print("Output Text: " + plaintext)
        return plaintext, mapping
    # Brute force solution with random mappings and filtering for common english words in output
    else:
        # Load words to search for
        wordList = loadWords(word_list)
        # accumulate words found, keyed by start index
        foundWords = defaultdict(list)
        for n in range(0, num_trials):
            random_out = random.sample(list(unused_out), k=len(unused_out))
            # assign un-mapped letters using random permutation of unassigned output letters
            for i, c in enumerate(unused_in):
                mapping[c] = random_out[i]
            plaintext = ciphertext.translate(str.maketrans(mapping))
            # search plaintext for valid words
            for i, w in enumerate(wordList):
                start = plaintext.find(w)
                if start != -1:
                    end = start + len(w)
                    if not silent:
                        print("Cipher Text:", ciphertext[0:start], ciphertext[start:end], ciphertext[end:])
                        print("Output Text:", plaintext[0:start], plaintext[start:end], plaintext[end:], "\n")
                    wordList.remove(w)  # avoid getting lots of repeated hits
                    foundWords[start].append(w)
        # sort by index ascending
        foundWords = OrderedDict(sorted(foundWords.items(), key=lambda t: t[0]))
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
    plaintext = plaintext.lower()
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
    for k, v in found.items():
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
    found = crackSub(cipher, mapping=m, mode="random", num_trials=1, word_list=0) # find words using freq map
    if found:
        print("Found Words:")
        printFW(found)

    # choose a subset of found words that do not conflict when assigning a map
    # plain_char => message_index
    chosen_map = {}
    for start, options in found.items(): # one forward pass through message only
        # check that this index isn't already assigned (word overlap)
        if start not in chosen_map.values():
            for word in options:
                for i, char in enumerate(word):
                    if char not in chosen_map:
                        # assign new plain_char to this index
                        chosen_map[char] = start + i
                    elif cipher[start + i] == cipher[chosen_map[char]]:
                        # compatible duplicate assignment, allow and move on to next char
                        continue
                    else:
                        # Conflict - roll back any assignments from this word, then try next word in words
                        for c in word:
                            chosen_map.pop(c,None)
                        break
    # save max(len(chosen_map)) & chosen_map & print spaced output (mode=f)
    print(len(chosen_map), "characters assigned")
    # convert chosen_map to {cipher => plain} char mapping
    m = {}
    for out_char, i in chosen_map.items():
        in_char = cipher[i]  # get cipher character at chosen index
        m[in_char] = out_char
    pprint(m.items())
    plain, m = crackSub(cipher, mapping=m, mode="f")
    print("Cipher Text: " + cipher)
    print("Output Text: " + plain)
    # find more words using freq map, by incrementing word_list
    found = crackSub(cipher, mapping=m, mode="random", num_trials=1, word_list=1, silent=False)
    ### NOTES ############################################################
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
    # Output can be further filtered using nltk to exclude grammatically-incorrect sentences
    #   - using ne_chunk(), @see http://nlpforhackers.io/named-entity-extraction/
    # Could also rank word n-grams by probability of correctness: @see http://nlpforhackers.io/language-models/