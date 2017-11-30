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

def cracksub(ciphertext, mode=0):
    relFreq = {}
    # remove whitespace for calculating relative frequencies
    no_ws_text = input_text.replace(string.whitespace, "")
    chars = len(no_ws_text)
    cnt = Counter(no_ws_text)
    for i in alphabet:
        relFreq[i] = (cnt[i] / chars)
    # order by frequency descending
    mfcs = OrderedDict(sorted(relFreq.items(),key=lambda t: t[1], reverse=True))
    print("Most Frequent cipher characters:")
    pprint(list(mfcs.keys()),compact=True)
    if mode == 0:
        # attempt naive replacement using english frequencies
        mapping = {} # encrypted char -> decrypted char
        c = 0
        for k in mfcs.keys():
            mapping[k] = standard_mfcs[c]
            c += 1
        decrypted = input_text.translate(str.maketrans(mapping))
        print("Cipher Text: " + input_text)
        print("Output Text: " + decrypted)
        return decrypted
    elif mode == 1:
        # guessing plus assigning leftovers by frequency
        # TODO accept dict input for mapping when mode == 1
        mapping = {'r': 's',
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
        unused_in = [x for x in mfcs.keys() if x not in mapping.keys()]
        unused_out = [x for x in standard_mfcs if x not in mapping.values()]
        c = 0
        for i in unused_in:
            mapping[i] = unused_out[c]
            c += 1
        decrypted = input_text.translate(str.maketrans(mapping))
        print("Cipher Text: " + input_text)
        print("Output Text: " + decrypted)
        return decrypted
    else:
        # Brute force solution with random mappings and filtering for common short words in output
        # TODO accept num for trials, and use below method (w/trials and filtering) when dict is provided
        perms = permutations(alphabet)
        for i in range(0, 5000000000):
            p = next(perms)
            #sample every fifth permutation (saving on time/memory with pseudo-random sampling)
            if i % 500 == 0:
                p = list(p)
                mapping = {}
                c = 0
                for k in mfcs.keys():
                    mapping[k] = p[c]
                    c += 1

                decrypted = input_text.translate(str.maketrans(mapping))
                for w in words:
                    if w in decrypted.split():  # split() can only be used if cipher contains spaces
                        print("Cipher Text: " + input_text)
                        print("Output Text: " + decrypted)
                        words.remove(w) # avoid getting lots of junk permutations on one "hit"
                        break
        return
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
    print(cracksub(input_text))
