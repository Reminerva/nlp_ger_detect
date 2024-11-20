import re
import spacy
import pandas as pd
import streamlit as st
from io import BytesIO
import xlsxwriter 

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

        return kalimat_perbandingan.append("Tidak ada kalimat perbandingan pada teks")

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

        return kalimat_lampau.append("Tidak ada kalimat lampau pada teks")

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

with st.sidebar:
    
    st.title('Detector Kalimat Perbandingan dan Lampau :sparkles:')
    # Menambahkan logo perusahaan
    st.image("https://learn.g2.com/hubfs/Imported%20sitepage%20images/1ZB5giUShe0gw9a6L69qAgsd7wKTQ60ZRoJC5Xq3BIXS517sL6i6mnkAN9khqnaIGzE6FASAusRr7w=w1439-h786.png")

st.title('Detector Kalimat Perbandingan dan Lampau :sparkles:')
# st.header('Proyek Data Analisis :sparkles:')
st.caption('Created by: Frau Devita Pratiwi')

# Kotak kosong buat diisi
teks_langsung = st.text_input("Masukkan teks:")
placeholder_langsung = st.empty()
placeholder_langsung_2 = st.empty()

# Upload file
uploaded_file = st.file_uploader("Pilih file .txt", type="txt")
placeholder_file = st.empty()

# Kalau ada dile yang di upload
if uploaded_file is not None:

    # Membuka file dan membaca isinya
    teks_dari_txt = ''.join(
        line.strip() + ' ' for line in uploaded_file.read().decode('utf-8').splitlines()).strip()

    df_main = get_data_frame(teks_dari_txt)
    placeholder_file.write(df_main)

    # Menyimpan DataFrame ke file Excel dalam memori
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, index=False, sheet_name='Sheet1')
        # writer.save()

    # Mendapatkan data file Excel
    excel_data = output.getvalue()

    # Tombol untuk mengunduh file Excel
    placeholder_file.download_button(
        label="Download File Excel",
        data=excel_data,
        file_name="Hasil deteksi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.write("Belum ada file yang diunggah.")

if teks_langsung == '':

    placeholder_langsung.empty()

else:

    df_main = get_data_frame(teks_langsung)
    placeholder_langsung.dataframe(df_main)

    # Menyimpan DataFrame ke file Excel dalam memori
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_main.to_excel(writer, index=False, sheet_name='Sheet1')
        # writer.save()

    # Mendapatkan data file Excel
    excel_data = output.getvalue()

    # Tombol untuk mengunduh file Excel
    placeholder_langsung_2.download_button(
        label="Download File Excel",
        data=excel_data,
        file_name="Hasil deteksi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if st.button("Hapus Semua Output"):
    placeholder_langsung.empty()
    placeholder_file.empty()
    placeholder_langsung_2.empty()