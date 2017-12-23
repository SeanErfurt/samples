import string
from collections import Counter, defaultdict, OrderedDict
from pprint import pprint
import random
import json
from nltk.corpus import stopwords, words
import phrasefinder  # @see https://github.com/mtrenkmann/phrasefinder-client-python

# set of possible keys (assumption)
alphabet = string.ascii_lowercase
# order of most frequent english characters
standard_mfcs = "etaoinshrdlucmfwypvbgkjqxz"
# parameters for the phrasefinder API client
params = phrasefinder.Options()
params.corpus = phrasefinder.Corpus.AmericanEnglish  # default
params.nmin = 1  # default
params.nmax = 3  # default = 5
params.topk = 100  # default
ngram_totals = [4362290, 120559663, 418881178]

def loadWords(word_list):
    """
    Load in the selected word list for searching in plaintext.
    :param word_list: int representing relatively-sized lists (1 == stop-words)
    :return: list of strings
    """
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
        fragments = {'s', 't', 'd', 'm', 'o', 'y', 've', 're', 'ain'}  # exclude, count as stop-words but aren't words
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
            wordList = w.read().splitlines()
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
def pf_query(query='I like ?'):
    """Queries the PhraseFinder web service and returns the result."""
    q = query
    result = []
    # Perform a request.
    try:
        response = phrasefinder.search(q, params)
        if response.status != phrasefinder.Status.Ok:
            print('Request was not successful: {}'.format(response.status))
            return result
        # Print phrases line by line.
        # TODO light pre-processing (relFreq, organizing, etc)
        for phrase in response.phrases:
            phrase_relFreq = phrase.match_count / ngram_totals[len(phrase.tokens) - 1]
            print("{0} {1:6f} {2:6f}".format(phrase.match_count, phrase.score, phrase_relFreq), end="")
            for token in phrase.tokens:
                print(' {}_{}'.format(token.text, token.tag), end="")
            print()
        # Example output:
        #   1065105 0.268530 0.002543 I_0 like_0 to_1
        #   484768 0.122218 0.001157 I_0 like_0 the_1
        #   ...
        # Token tag meaning:
        # 0 => Given
        # 1 => Inserted
        # 2 => Alternative
        # 3 => Completed
    except Exception as error:
        # Catch-all for connection issues, malformed query, something else unforseen
        print('Some error occurred: {}'.format(error))
    return result

# TODO sample sufficient google ngram data to build an accurate n-gram Markov model

# TODO build n-gram model using data collected above (@see http://nlpforhackers.io/language-models/)

# TODO use n-gram model to "fill in" the spaces in incomplete decyphered text, then validate the resultant mapping

# TODO Calculate probability of "filled" decyphered text using n-gram model (up to n=3) with "stupid" back-off smoothing

# TODO Rank list of valid candidate plaintexts by probability using smoothed n-gram model


def crackSub(ciphertext, mapping=None, ignore_ws=True, silent=True):
    """
    Solves an arbitrary substitution cipher using randomization and NLP
    :param ciphertext: the encoded message to crack
    :param mapping: optional dictionary with cipher => plain character mappings
    :param ignore_ws: whether to ignore original whitespace in message (default) or keep it
    :param silent: if True (default), suppress output to stdout where possible
    :return: the decoded message and the character mapping used
    """
    # TODO add support for user-given alphabets (both in and out)
    # sanitization
    ciphertext = ciphertext.lower()
    if ignore_ws:
        ciphertext = ''.join(ciphertext.split())
    if mapping is None:
        # initialize with frequency mapping
        plaintext, mapping = decodeSub(ciphertext, mode="freq", silent=silent)

    # find more words by using progressively larger word lists, using standard_mfcs to fill gaps in mappings
    for word_list in range(5):
        found = decodeSub(ciphertext, mapping=mapping, mode="random", word_list=word_list, silent=silent)
        # run getMapping for each "first word" in the found dict, and select maximal mapping from resulting candidates
        if len(found[list(found.keys())[0]]) > 1:
            max_map = {}
            for first_word in range(len(found[list(found.keys())[0]])):
                m = getMappingFromWords(found, ciphertext, silent=silent)
                if len(m) > len(max_map):
                    max_map = m
                found[list(found.keys())[0]][first_word] = ""
            mapping = max_map
        else:
            mapping = getMappingFromWords(found, ciphertext, silent=silent)
        plaintext, mapping = decodeSub(ciphertext, mapping=mapping, mode="freq", silent=silent)
        if not silent:
            print("[ Results using word list", word_list, "]")
            print("Mapping: ", end="")
            pprint(mapping.items())
            print("Cipher Text: " + ciphertext)
            print("Output Text: " + plaintext)
    return plaintext, mapping

    # TODO create mutations in mapping to avoid getting stuck on incorrect char mappings / words
    # TODO once we have 50% valid words, fill in remaining spaces in message using n-gram phrase expansion
    #       can also possibly generate new candidate messages using random subset of found words and then expanding
    # if there are multiple possible messages after looping, rank them using n-gram model probabilities, then output
    # Output can be augmented/filtered using nltk to exclude grammatically-incorrect sentences, or generate candidates
    #   - using ne_chunk(), @see http://nlpforhackers.io/named-entity-extraction/
    # Could also rank word n-grams by probability of correctness: @see http://nlpforhackers.io/language-models/

def decodeSub(ciphertext, mode="frequency", mapping=None, word_list=0, silent=True):
    """
    Attempt to decode a substitution cipher using a given, frequency-based or random character mapping.
    :param ciphertext: the encoded message as a string
    :param mode: whether to use standard English character frequencies (default) or random mapping
    :param mapping: optional dictionary with cipher => plain character mappings
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
    # Attempt random mapping and search for common english words in output to inform next decoding attempt
    else:
        # sample unused letters in alphabet for random order
        random_out = random.sample(list(unused_out), k=len(unused_out))
        # assign un-mapped letters using random permutation of unassigned output letters
        for i, c in enumerate(unused_in):
            mapping[c] = random_out[i]
        plaintext = ciphertext.translate(str.maketrans(mapping))
        foundWords = findWords(plaintext, word_list, ciphertext, silent)
        if not silent:
            printFW(foundWords)
        return foundWords


def encodeSub(plaintext, mapping=None):
    """
    Use a substitution cipher to encode a message.
    :param plaintext: the message to encode
    :param mapping: optional dictionary to use when encoding
    :return: [encoded message, {mapping}]
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

def findWords(plaintext, word_list, ciphertext=None, silent=True):
    """
    Searches given plaintext for valid words from given word list
    :param plaintext:  the partially decoded text to search through
    :param word_list:  an integer representing the word list to use for searching
    :param ciphertext:  the original text being decoded (only needed if silent == False)
    :param silent:  whether to output the found words within message context
    :return: an OrderedDict containing the found words keyed on their start index within the message
    """
    # Load words to search for
    wordList = loadWords(word_list)
    # accumulate words found, keyed by start index
    foundWords = defaultdict(list)
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

def printFW(found):
    """
    Pretty-print the found words dictionary.
    :param found: dict
    """
    if found:
        print("Found Words:")
        for k, v in found.items():
            print(k, end='\t')
            pprint(v)
    else:
        print(None)


def getMappingFromWords(foundWords, cipher, silent=False):
    """
    Choose a subset of found words that do not conflict when assigned to a mapping
    :param foundWords: OrderedDict keyed on message index. Values are a list of possible words starting at that index.
    :param cipher: The original ciphertext, for checking conflicts and adding keys to output mapping
    :param silent: if True, suppress debug output
    :return: a valid dict mapping to pass to decodeSub()
    """
    # plain_char => message_index
    chosen_map = {}
    for start, options in foundWords.items():  # one forward pass through message only (change?)
        # check that this index isn't already assigned (word overlap)
        if start not in chosen_map.values():
            for word in options:
                compat = set()
                for i, char in enumerate(word):
                    if char not in chosen_map:
                        # assign new plain_char to this index
                        chosen_map[char] = start + i
                    elif cipher[start + i] == cipher[chosen_map[char]]:
                        # compatible duplicate assignment, allow and move on to next char
                        compat.add(char)
                        continue
                    else:
                        # Conflict - roll back any new char assignments from this word, then try next word in words
                        for c in word:
                            if c != char and c not in compat: # don't remove assignments that existed before this word
                                chosen_map.pop(c, None)
                        break
    # convert chosen_map to {cipher => plain} char mapping
    m = {}
    for out_char, i in chosen_map.items():
        in_char = cipher[i]  # get cipher character at chosen index
        m[in_char] = out_char
    if not silent:
        print(len(m), "characters assigned")
        pprint(m.items())
    return m


if __name__ == "__main__":
    #print(pf_query())
    #quit()
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
    print(crackSub(cipher, mapping=None, ignore_ws=True, silent=False))

    # Example output (with spaces added manually) ##########################
    # a csomerufd iereonty hai tageo bsiieiinso su ly eotnre isfd dnge theie
    # iceet lsronopi su ibrnop chnwh n eozsy cnth ly chsde heart n al adsoe
    # aom ueed the wharl su ejniteowe no thni ibst chnwh cai wreatem usr
    # the vdnii su isfdi dnge lnoe n al is habby ly mear urneom is avisrvem
    # no the ejxfninte ieoie su lere traoxfnd ejniteowe that n oepdewt ly
    # tadeoti n ihsfdm ve nowabavde su mracnop a inopde itrsge at the
    # breieot lsleot aom yet n ueed that n oeker cai a preater artnit thao
    # osc cheo chnde the dskedy kaddey teeli cnth kabsfr arsfom le aom the
    # lernmnao ifo itrngei the fbber ifruawe su the nlbeoetravde usdnape
    # su ly treei aom vft a uec itray pdeali itead nots the nooer
    # iaowtfary n thrsc lyiedu msco alsop the tadd praii vy the trnwgdnop
    # itreal aom ai n dne wdsie ts the earth a thsfiaom fogosco bdaoti
    # are ostnwem vy le cheo n hear the vfqq su the dnttde csrdm alsop
    # the itadgi aom prsc ualndnar cnth the wsfotdeii nomeiwrnvavde usrli
    # su the noiewti aom udnei theo n ueed the breieowe su the adlnphty
    # chs usrlem fi no hni sco nlape aom the vreath
    ########################################################################
    # Note that even without any NLP enhancements, the random + word search
    #  method was able to fully recover the mapping for the letters in "heart",
    # producing 6 different words, and partially "breath"(vreath), "happy"(habby),
    # and "greater"(preater). If spaces are preserved in the input, the accuracy
    # will likely be even better. Still, right now the output doesn't contain
    # enough real words to use n-gram phrase expansion to uncover the rest.

    # Some incredibly common short words were absent from the final output,
    # like "I", "am", "of", "and", and "my", even though it should have preferred
    # to find these words over longer, less common words like "heart". Maybe
    # mutating the character mappings from this stage and culling the mutations
    # based on percentage of valid words in output will get us even further.

    # Once we have about 50% valid words in the output, we can attempt phrase
    # expansion to get us the rest of the way, possibly with mutations at the
    # word level to avoid getting stuck on a local maximum of valid words.

    # When we can create multiple fully-decoded message candidates, we can then
    # rank them using the n-gram model and output the ranked results for human
    # validation as the final step in decryption, as some will likely be nonsense,
    # but in a way that is difficult for a program to detect.
