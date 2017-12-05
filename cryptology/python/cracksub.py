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
        fragments = set(['s', 't', 'd', 'm', 'o', 'y', 've', 're','ain']) # exclude, count as stop-words but aren't words
        wordList = [w for w in stopwords.words('english') if w not in fragments]
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

# TODO load in or query google ngram viewer data for bigram/trigram frequencies
# @see https://storage.googleapis.com/books/ngrams/books/datasetsv2.html

# TODO Alternative to downloading google ngram viewer data:
# @see http://phrasefinder.io/documentation
# @see https://github.com/mtrenkmann/phrasefinder-client-python
# Bonuses of this method: sums absFreq of n-gram across all years (saves lots of time and calcs)
#                         gives relative frequencies within query result set (good for phrase expansion)
#                         dont need to download massive amounts of data
#       For overall relFreq within corpus, use totals (reproduced below)
#             1-grams:   4,362,290
#             2-grams: 120,559,663
#             3-grams: 418,881,178
#             4-grams: 584,347,976
#             5-grams: 448,506,094

# TODO sample sufficient google ngram data to build an accurate n-gram Markov model

# TODO build n-gram model using data collected above (@see http://nlpforhackers.io/language-models/)

# TODO use n-gram model to "fill in" the spaces in incomplete decyphered text, then validate the resultant mapping

# TODO Calculate probability of "filled" decyphered text using n-gram model (up to n=3) with "stupid" backoff smoothing

# TODO Rank list of valid candidate plaintexts by probability using smoothed n-gram model

def crackSub(ciphertext, mode="frequency", num_trials=100000, mapping=None, ignore_ws=True, word_list=0, silent=True):
    """
    Attempt to crack a substitution cipher.
    :param ciphertext: the encoded message as a string
    :param mode: whether to use standard English character frequencies (default) or random mapping
    :param num_trials: number of trials to run if using random mappings (default is 1000000)
    :param mapping: optional dictionary with cipher => plain character mappings
    :param ignore_ws: whether to ignore original whitespace in message (default) or keep it
    :param word_list: the list of words to search for in output { (s)hort | (m)edium | (l)ong }
    :param silent: if True (default), suppress output to stdout
    :return: if frequency mode, the plaintext generated and mapping used. Else, potential word mappings to use.
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
    # TODO actually support retaining whitespace if given (can be a helpful clue)
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
            for w in wordList:
                start = plaintext.find(w)
                if start != -1:
                    if not silent:
                        end = start + len(w)
                        print("Cipher Text:", ciphertext[0:start], ciphertext[start:end], ciphertext[end:])
                        print("Output Text:", plaintext[0:start], plaintext[start:end], plaintext[end:], "\n")
                    wordList.remove(w)  # avoid getting lots of repeated hits (change?)
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
    # sanitization
    plaintext = plaintext.lower()
    plaintext = ''.join(c for c in plaintext if c.isalpha())
    # if there is no mapping or if the mapping is incomplete, generate a new one randomly
    if not (mapping and len(mapping.keys()) == len(alphabet)):
        random_out = random.sample(list(alphabet), k=len(alphabet))
        for i, c in enumerate(alphabet):
            mapping[c] = random_out[i]
    ciphertext = plaintext.translate(str.maketrans(mapping))
    return ciphertext, mapping


def printFW(found):
    '''
    Pretty-print the found words dictionary.
    :param found: dict
    '''
    if found:
        print("Found Words:")
        for k, v in found.items():
            print(k, end='\t')
            pprint(v)
    else:
        print(None)


if __name__ == "__main__":
    # message = 'The quick brown fox jumps over the lazy dog'
    message = '''A wonderful serenity has taken possession of my entire soul, like these sweet mornings of spring 
    which I enjoy with my whole heart. I am alone, and feel the charm of existence in this spot, which was created 
    for the bliss of souls like mine. I am so happy, my dear friend, so absorbed in the exquisite sense of mere 
    tranquil existence, that I neglect my talents. I should be incapable of drawing a single stroke at the present 
    moment; and yet I feel that I never was a greater artist than now. When, while the lovely valley teems with 
    vapour around me, and the meridian sun strikes the upper surface of the impenetrable foliage of my trees, 
    and but a few stray gleams steal into the inner sanctuary, I throw myself down among the tall grass by the 
    trickling stream; and, as I lie close to the earth, a thousand unknown plants are noticed by me: when I hear the 
    buzz of the little world among the stalks, and grow familiar with the countless indescribable forms of the 
    insects and flies, then I feel the presence of the Almighty, who formed us in his own image, and the breath '''
    try:
        with open("subAnswer.txt", mode="r") as answers:
            mapping_answer = json.load(answers)
            cipher, _ = encodeSub(message, mapping_answer)
    except:
        with open("subAnswer.txt", mode="w") as answers:
            cipher, mapping_answer = encodeSub(message)
            answers.write(json.dumps(mapping_answer))

    # TODO "loop-ify" to get possible messages to send to grammar validation using NLP: NER/chunking/n-grams/something
    plain, m = crackSub(cipher, mode="f") # get frequency mapping
    found = crackSub(cipher, mapping=m, mode="random", num_trials=1, word_list=0) # find words using freq map
    printFW(found)
    # TODO extract getMappingFromWords method
    # choose a subset of found words that do not conflict when assigned to a mapping
    # plain_char => message_index
    chosen_map = {}
    for start, options in found.items(): # one forward pass through message only (change?)
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
    # TODO save max(len(chosen_map)) & chosen_map & print spaced output (mode=f)
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
    # find more words using freq map, by incrementing word_list (loop starts again here)
    found = crackSub(cipher, mapping=m, mode="random", num_trials=1, word_list=1, silent=False)
    printFW(found)
    # TODO after word_list == 4 is used, fill in remaining spaces using n-gram phrase expansion
    # if there are multiple possible messages, rank them using n-gram model probabilities, then output

    ### NOTES ############################################################
    # TODO Automate the word-finding/map-building to decode an arbitrary ciphertext
    # Top-level iter: found = crackSub(cipher, mapping=m, mode="random", num_trials=50, wordList="m")
    #       use found tree to make educated guesses in mapping, then iterate until a message appears
    # While message contains non-words (run crackSub in freq mode for output), run some trials and collect options
    # select word combinations that do not overlap from found options:
    #   e.g. message_i = 0,j=0, select found[m_i][j], assign map according to each char in found[m_i][j]
    #   then set message_i = m_i + len(found[m_i][j] and j=0 and select found[m_i][j] again, but
    #   if new found[m_i][j] has a conflicting assignment (in- or out-char is not in set(unused_in) or set(u_out), then
    #   remove any intermediate assignments from invalid words & try the next found[m_i][j++] until it does not conflict
    # If we run out of words to try before we reach the end of the message, save max(m_i) & mapping, print spaced output
    # Then message_i = 0 again and try the next found[0][j++]. Repeat until found[0] has all been tried.
    # Whichever word combination used the most letters will be output, and that char mapping is used for next trials.
    # Expand wordList with each loop to find new, less common, larger words now that mapping is bootstrapped.
    # ISSUE: this seems ok, but favors short words & words near the start heavily. Could get stuck on wrong words.
    # SOLUTION(?): Mutate by randomly choosing only some of the words/mapping to use, using n-gram model for fitness
    # Output can be augmented/filtered using nltk to exclude grammatically-incorrect sentences, or generate candidates
    #   - using ne_chunk(), @see http://nlpforhackers.io/named-entity-extraction/
    # Could also rank word n-grams by probability of correctness: @see http://nlpforhackers.io/language-models/