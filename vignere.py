import streamlit as st
import re
from collections import Counter
import string

# -------------------------------
# Setup
# -------------------------------
ALPHABET = string.ascii_uppercase
A2I = {c: i for i, c in enumerate(ALPHABET)}
I2A = {i: c for i, c in enumerate(ALPHABET)}

# -------------------------------
# 1. Kasiski Examination
# -------------------------------
def kasiski(cipher, min_len=3):
    repeats = {}
    for size in range(min_len, 6):  # sequences of length 3-5
        for i in range(len(cipher) - size):
            seq = cipher[i:i+size]
            for j in range(i+1, len(cipher) - size):
                if cipher[j:j+size] == seq:
                    repeats.setdefault(seq, []).append(j - i)
    return repeats

# -------------------------------
# 2. Index of Coincidence
# -------------------------------
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

# -------------------------------
# 3. Frequency Analysis
# -------------------------------
def caesar_shift_from_freq(text):
    if not text:
        return 0
    freqs = Counter(text)
    most_common_letter = freqs.most_common(1)[0][0]
    shift = (A2I[most_common_letter] - A2I['E']) % 26
    return shift

# -------------------------------
# 4. Key Recovery and Decryption
# -------------------------------
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

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🔐 Vigenère Cipher Solver")
st.write("Paste your ciphertext below. This tool will analyze it, estimate the key, and decrypt it.")

ciphertext_input = st.text_area(
    "Ciphertext (letters only)", 
    height=150
)

max_key_len = st.number_input(
    "Maximum key length to test (for IC analysis):", 
    min_value=5, max_value=50, value=20
)

if st.button("Analyze & Decrypt"):
    cipher = re.sub(r'[^A-Z]', '', ciphertext_input.upper())
    if len(cipher) < 3:
        st.error("Ciphertext is too short!")
    else:
        # Kasiski
        st.subheader("🔎 Kasiski Examination")
        rep = kasiski(cipher)
        if rep:
            for seq, dist in rep.items():
                st.write(f"**{seq}** → distances: {dist}")
        else:
            st.write("No repeated sequences found.")

        # Friedman
        st.subheader("📈 Friedman Test (Index of Coincidence)")
        ic = friedman(cipher, max_key_len)
        st.write(ic)

        # Likely key length
        likely = max(ic, key=ic.get)
        st.subheader("🎯 Estimated Key Length")
        st.write(f"**Likely key length:** {likely}")

        # Key recovery
        key = recover_key(cipher, likely)
        st.subheader("🔑 Recovered Key")
        st.write(f"**{key}**")

        # Decryption
        plaintext = vigenere_decrypt(cipher, key)
        st.subheader("📝 Decrypted Plaintext")
        st.write(plaintext)
