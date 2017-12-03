import string
from collections import Counter, OrderedDict, defaultdict
from pprint import pprint
from itertools import permutations
import random


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

def cracksub(ciphertext, mode=0, num_trials=1000000, mapping={}, ignore_ws=False):
    relFreq = {}
    # remove whitespace for calculating relative frequencies
    no_ws_text = ''.join(ciphertext.split())
    if ignore_ws:
        ciphertext = no_ws_text
    #TODO extract method getMFCs
    chars = len(no_ws_text)
    cnt = Counter(no_ws_text)
    for i in alphabet:
        relFreq[i] = (cnt[i] / chars)
    # order by frequency descending
    mfcs = OrderedDict(sorted(relFreq.items(),key=lambda t: t[1], reverse=True))
    print("Most Frequent cipher characters:")
    pprint(list(mfcs.keys()), compact=True)
    # Find un-mapped letters
    unused_in = [x for x in mfcs.keys() if x not in mapping.keys()]
    unused_out = [x for x in standard_mfcs if x not in mapping.values()]
    # Frequency-based mapping
    if mode == 0:
        # assign un-mapped letters in order
        for i, c in enumerate(unused_in):
            mapping[c] = unused_out[i]
        decrypted = ciphertext.translate(str.maketrans(mapping))
        print("Cipher Text: " + ciphertext)
        print("Output Text: " + decrypted)
        return decrypted
    else:
        # Brute force solution with random mappings and filtering for common short words in output
        found = defaultdict(list)
        print("Cipher Text: " + ciphertext)
        for i in range(0, num_trials):
            random_out = random.sample(list(unused_out), k=len(unused_out))
            # assign un-mapped letters using random permutation of unassigned output letters
            for i, c in enumerate(unused_in):
                mapping[c] = random_out[i]
            decrypted = ciphertext.translate(str.maketrans(mapping))
            # TODO: Extract Method findWords
            for w in words:
                index = decrypted.find(w)
                if index != -1:
                    print("Output Text: " + decrypted)
                    cipher = ciphertext[index:index + len(w)]
                    found[cipher].append(w)
                    words.remove(w)  # avoid getting lots of junk permutations on one "hit"
                    break
        return found


if __name__ == "__main__":
    input_text = "zqw popy rcd njb hd hq lj lnpc dpv dttlf c uujskv bjuj jfusgf foe nkjt mmu rzhr rj roc uczsq " \
                 "jpqjglb adfgic "
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
    print(cracksub(input_text, mapping=m, mode=1, ignore_ws=False))
