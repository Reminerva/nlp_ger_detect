import re
import spacy
import pandas as pd
import streamlit as st

teks = "abber als sdfjkdf"

# # Unggah file
# uploaded = files.upload()

# # Menampilkan nama file yang diunggah
# for file_name in uploaded.keys():
#     print(f"File yang diunggah: {file_name}")
#     file_name = file_name

# # Membuka file dan membaca isinya
# with open(file_name, 'r', encoding='utf-8') as file:
#     teks = file.read()

# with open(file_name, 'r', encoding='utf-8') as file:
#     teks = ''.join(line.strip() + ' ' for line in file).strip()

# Load spaCy model untuk analisis tata bahasa
nlp = spacy.load("de_core_news_sm")
nlp.max_length = 2000000


# Fungsi untuk mendeteksi kalimat perbandingan
def deteksi_perbandingan(teks):

    corpus = nlp(teks)
    kalimat_perbandingan = []
    pola_komparatif = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat

        pola_komparatif.append(re.findall(r'\w+er als ', kalimat.text.lower())) # Pola Komparativ + als
        pola_komparatif.append(re.findall(r'mehr \w+ als ', kalimat.text.lower())) # Pola Mehr + Komparativ + als


        if pola_komparatif != [[],[]]: # Periksa apakah ada Pola Komparativ

            kalimat_perbandingan.append(kalimat.text)

        pola_komparatif = []

    if kalimat_perbandingan == []:

        return "Tidak ada kalimat perbandingan pada teks"

    else:

        return (kalimat_perbandingan)


# Fungsi untuk mendeteksi kalimat lampau
def deteksi_lampau(teks):

    corpus = nlp(teks)
    kalimat_lampau = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat

        if "als " in kalimat.text.lower(): # Periksa apakah ada "als"

            kata_kerja = []

            for token in kalimat: # Iterasi setiap token dalam kalimat

                if token.pos_ == "VERB" and token.tag_ in ["VVFIN", "VAFIN"]:

                    kata_kerja.append(token)

            if len(kata_kerja) > 0: # Pastikan ada kata kerja

                kalimat_lampau.append(kalimat.text)

    if kalimat_lampau == []:

        return "Tidak ada kalimat lampau pada teks"

    else:

        return (kalimat_lampau)

def program_utama(teks):

    a = deteksi_perbandingan(teks)
    b = deteksi_lampau(teks)

    if len(a) < len(b):

        for i in range (len(b)-len(a)):

            a.append(None)

    elif len(b) < len(a):

        for i in range (len(a)-len(b)):

            b.append(None)

    return a, b

def get_data_frame(teks):

    hasil = {'kalimat_perbandingan' : program_utama(teks)[0], 'kalimat_lampau' : program_utama(teks)[1]}

    df_main = pd.DataFrame(data = hasil)

    return df_main

def df_to_excel(df_main):

    df_main.to_excel('Hasil deteksi.xlsx')

st.sidebar()