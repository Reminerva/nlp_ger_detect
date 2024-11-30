import spacy
import pandas as pd
import streamlit as st
from io import BytesIO
import xlsxwriter 
import base64
import pdfplumber


# Load spaCy model untuk analisis tata bahasa
nlp = spacy.load("de_core_news_sm")
nlp.max_length = 2000000



# Fungsi untuk mendeteksi kalimat perbandingan
def deteksi_perbandingan(teks):

    corpus = nlp(teks)
    kalimat_perbandingan = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat
        
        pola_komparatif = []

        # pola_komparatif.append(re.findall(r'\w+er als ', kalimat.text.lower())) # Pola Komparativ + als
        # pola_komparatif.append(re.findall(r'mehr \w+ als ', kalimat.text.lower())) # Pola Mehr + Komparativ + als

        if 'als ' in kalimat.text.lower(): # Periksa apakah ada 'als

            for i, token in enumerate(kalimat): # Iterasi setiap token dalam kalimat

                if token.text == 'als' and kalimat[i-1].tag_ == "ADJD":

                    pola_komparatif.append(token)

                if token.text.lower() == 'als' and kalimat[i-1].text.lower() == 'mehr' or kalimat[i-1].text.lower() == 'weniger' :

                    pola_komparatif.append(token)

                if token.text == 'als' and kalimat[i-2].tag_ == "ADJA" or kalimat[i-2].text == 'mehr' or kalimat[i-2].text == 'lieber': # Tag ADJA sbg adjektiv (komparativ) atributif

                    pola_komparatif.append(token)

            if len(pola_komparatif) > 0: # Pastikan ada pola komparatif

                kalimat_perbandingan.append(kalimat.text)

    if kalimat_perbandingan == []:
        
        kalimat_perbandingan.append("Tidak ada kalimat perbandingan pada teks")

        return kalimat_perbandingan
    
    else:

        return list(set(kalimat_perbandingan))

# Fungsi untuk mendeteksi kalimat lampau
def deteksi_lampau(teks):

    corpus = nlp(teks)
    kalimat_lampau = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat

        pola_lampau = []

        if "als " in kalimat.text.lower(): # Periksa apakah ada "als"

            for i, token in enumerate(kalimat):

                if kalimat[0].text == 'Als'and kalimat[1].pos_ in ["PRON","NOUN"] and token.text == "," and kalimat[i-1].pos_ in ["VERB", "AUX"]:

                    pola_lampau.append(token)
                
                elif token.text == 'als'and kalimat[i + 1].pos_ in ["PRON","NOUN"] and kalimat[-2].pos_ in ["VERB", "AUX"]:

                    pola_lampau.append(token)

            if len(pola_lampau) > 0: # Pastikan ada kata kerja

                kalimat_lampau.append(kalimat.text)

    if kalimat_lampau == []:
        
        kalimat_lampau.append("Tidak ada kalimat lampau pada teks")

        return kalimat_lampau
    
    else:

        return list(set(kalimat_lampau))

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

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()






# CODE UNTUK TAMPILAN WEB (USER INTERFACE)

img = get_img_as_base64("foto.jpg")

page_bg_img = f"""
<style>

[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}

</style>
"""
# page_bg_img = f"""
# <style>

# [data-testid="stAppViewContainer"] {{
# background-color: white;
# background-position: center; 
# background-repeat: no-repeat;
# background-attachment: fixed;
# }}

# </style>
# """

st.markdown(page_bg_img, unsafe_allow_html=True)


st.title('Detector Kalimat Perbandingan dan Lampau :sparkles:')
# st.header('Proyek Data Analisis :sparkles:')
st.caption('Created by: ')

with st.sidebar:
    
    st.title('Detector Kalimat Perbandingan dan Lampau :sparkles:')
    # Menambahkan logo perusahaan
    # st.image("https://learn.g2.com/hubfs/Imported%20sitepage%20images/1ZB5giUShe0gw9a6L69qAgsd7wKTQ60ZRoJC5Xq3BIXS517sL6i6mnkAN9khqnaIGzE6FASAusRr7w=w1439-h786.png")

# Kotak kosong buat diisi
teks_langsung = st.text_input("Masukkan teks:")
placeholder_langsung = st.empty()
placeholder_langsung_2 = st.empty()

# Upload file
uploaded_file = st.file_uploader("Pilih file .txt", type=["txt","pdf"])
placeholder_file = st.empty()
placeholder_file_teks = st.empty()

# Kalau ada dile yang di upload
df_main = ""
teks_dari_file = ""
if uploaded_file is not None:

    # try:
    # st.write(uploaded_file.type)

    if uploaded_file.type == "text/plain": ### READ FILE TXT

        # Membuka file dan membaca isinya
        teks_dari_file = ''.join(
            line.strip() + ' ' for line in uploaded_file.read().decode('utf-8').splitlines()).strip()

    elif uploaded_file.type == "application/pdf": ### READ FILE TXT

        with pdfplumber.open(uploaded_file) as pdf:
            num_pages = len(pdf.pages)

        # Menampilkan isi setiap halaman
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()

            teks_dari_file = teks_dari_file + text

            # st.subheader(f"Page {page_num + 1}")
        teks_dari_file = ''.join(
            line.strip() + ' ' for line in (teks_dari_file).splitlines()).strip()

    else:
        
        st.write("File tidak berhasil di read")

    # except Exception as e:

    #     st.error(f"Error reading the PDF file: {e}")
    
    df_main = get_data_frame(teks_dari_file)
    placeholder_file_teks.write(df_main)

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
    placeholder_file_teks.empty()

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