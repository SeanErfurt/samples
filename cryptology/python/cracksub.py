import string
from collections import Counter, OrderedDict
from pprint import pprint
from itertools import permutations
import random

input_text = "zqw popy rcd njb hd hq lj lnpc dpv dttlf c uujskv bjuj jfusgf foe nkjt mmu rzhr rj roc uczsq jpqjglb " \
             "adfgic"
# set of possible keys (assumption)
alphabet = string.ascii_lowercase
# order of most frequent english characters
standard_mfcs = "etaoinshrdlucmfwypvbgkjqxz"
# common short words to look for when validating possible decrytions
words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 'her',
         'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new',
         'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say',
         'she', 'too', 'use']

# Notes
# C = A or I
# (T, U, M) -> (s, e, t, f, l, m, o)
# HD, HQ -> (in, it, is, if); (of, or, on); (as, at, an, am); (be, by); (me, my)
# LJ, RJ -> (to, so, do, go, no); (of, if); (in, on, an); (it, at); (is, as, us); (be, we, he, me); (by, my)
# MMU -> eel, eek, ooh
#   (RCD, ROC, DPV, FOE) ->
#    ONE  OWN  E__  _W_
#    OLD  OWL?
#    LET  LIE  T__  _I_
#    PAD  PEA       _E
#    BA_  BRA
#    SA_  SEA
#    TA_  TEA
##############################################################3

def cracksub(ciphertext, mode=0, num_trials=1000000, mapping={}):
    relFreq = {}
    # remove whitespace for calculating relative frequencies
    no_ws_text = ''.join(input_text.split())
    print(no_ws_text)
    chars = len(no_ws_text)
    cnt = Counter(no_ws_text)
    for i in alphabet:
        relFreq[i] = (cnt[i] / chars)
    # order by frequency descending
    mfcs = OrderedDict(sorted(relFreq.items(),key=lambda t: t[1], reverse=True))
    print("Most Frequent cipher characters:")
    pprint(list(mfcs.keys()))
    # Find un-mapped letters
    unused_in = [x for x in mfcs.keys() if x not in mapping.keys()]
    unused_out = [x for x in standard_mfcs if x not in mapping.values()]
    # Frequency-based mapping
    if mode == 0:
        # assign un-mapped letters in order
        for i, c in enumerate(unused_in):
            mapping[c] = unused_out[i]
        decrypted = input_text.translate(str.maketrans(mapping))
        print("Cipher Text: " + input_text)
        print("Output Text: " + decrypted)
        return decrypted
    else:
        # Brute force solution with random mappings and filtering for common short words in output
        found = []
        print("Cipher Text: " + input_text)
        for i in range(0, num_trials):
            random_out = random.sample(list(unused_out), k=len(unused_out))
            # assign un-mapped letters using random permutation of unassigned output letters
            for i, c in enumerate(unused_in):
                mapping[c] = random_out[i]
            decrypted = input_text.translate(str.maketrans(mapping))
            # TODO: Add flag for ignoring given word boundaries (could be misleading)
            #decrypted = no_ws_text.translate(str.maketrans(mapping))
            for w in words:
                if w in decrypted.split():  # split() can only be used if cipher contains spaces
                    print("Output Text: " + decrypted)
                    # TODO: collect mapping that produces the found word
                    #for char in w:
                    #    pass
                    found.append(w)
                    words.remove(w) # avoid getting lots of junk permutations on one "hit"
                    break
        return found
    # Hybrid guessing and randomized ######################################
    # Input educated guess for some letters, fill other slots at random
    # mapping = {'r':'l', 'c':'e', 'd':'t', 'o':'i', 'f':'h', 'e':'s'}
    # unused_in = set(alphabet) - set(mapping.keys())
    # unused_out = set(alphabet) - set(mapping.values())
    # unused_out = random.sample(list(unused_out), k=len(unused_out))
    # c = 0
    # for i in unused_in:
    #     mapping[i] = unused_out[c]
    #     c += 1
    # decrypted = input_text.translate(str.maketrans(mapping))
    # print(input_text)
    # return decrypted


if __name__ == "__main__":
    m= {'r': 's',
        'c': 'a',
        'd': 'd',
        # 'o': 'r',
        # 'f': 'h',
        # 'e': 'r',
        'j': 'r',  # 't',
        'u': 'e',  # 'h',  # 'o',
        's': 'i',  # 'u',
        'g': 'g',
        # 'm': 'o',
        'k': 'l',
        'v': 'y',
        'p': 'a'
        }
    print(cracksub(input_text, mapping=m, mode=1))
