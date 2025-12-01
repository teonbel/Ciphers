import streamlit as st
import re
from collections import Counter
import string

ALPHABET = string.ascii_uppercase
A2I = {c: i for i, c in enumerate(ALPHABET)}
I2A = {i: c for i, c in enumerate(ALPHABET)}

###############################################################
# Vigenère Crypto Functions
###############################################################

def kasiski(cipher, min_len=3):
    repeats = {}
    for size in range(min_len, 6):
        for i in range(len(cipher) - size):
            seq = cipher[i:i+size]
            for j in range(i+1, len(cipher) - size):
                if cipher[j:j+size] == seq:
                    repeats.setdefault(seq, []).append(j - i)
    return repeats


def index_of_coincidence(text):
    N = len(text)
    if N <= 1:
        return 0
    freqs = Counter(text)
    num = sum(f * (f - 1) for f in freqs.values())
    den = N * (N - 1)
    return num / den


def friedman(cipher, max_key_length=20):
    ic_values = {}
    for k in range(1, max_key_length + 1):
        columns = [''.join(cipher[i] for i in range(j, len(cipher), k))
                   for j in range(k)]
        avg_ic = sum(index_of_coincidence(col) for col in columns) / k
        ic_values[k] = avg_ic
    return ic_values


def caesar_shift_from_freq(text):
    if not text:
        return 0
    freqs = Counter(text)
    most_common_letter = freqs.most_common(1)[0][0]
    shift = (A2I[most_common_letter] - A2I['E']) % 26
    return shift


def recover_key(cipher, key_len):
    columns = [''.join(cipher[i] for i in range(j, len(cipher), key_len))
               for j in range(key_len)]
    shifts = [caesar_shift_from_freq(col) for col in columns]
    key = ''.join(I2A[s] for s in shifts)
    return key


def vigenere_decrypt(cipher, key):
    plaintext = []
    key_nums = [A2I[c] for c in key]
    k = len(key)
    for i, c in enumerate(cipher):
        p = (A2I[c] - key_nums[i % k]) % 26
        plaintext.append(I2A[p])
    return ''.join(plaintext)


###############################################################
# Streamlit UI
###############################################################
import streamlit as st

st.title("Vigenère Solver")

