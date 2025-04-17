import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sklearn.linear_model import LinearRegression
import numpy as np

import google.generativeai as genai

# Konfigurasi API Key dari secrets.toml
genai.configure(api_key=st.secrets["GEMINI_API"])

# Fungsi untuk mengirim prompt ke Gemini
def getRespon(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Gunakan 'gemini-1.5-pro' jika tersedia
    response = model.generate_content(prompt)
    return response.text

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Judul Aplikasi
st.title("📊 Air Quality Monitoring Dashboard")
st.text("UNI328 - Burasa Daun Pisang")
st.markdown("""
Visualisasi data sensor DHT11 dari MongoDB & Rekomendasi Penyiraman Tanaman
""")

# Sidebar untuk filter data
with st.sidebar:
    st.header("Filter Data")
    hours_to_display = st.slider(
        "Tampilkan data berapa jam terakhir?",
        min_value=1,
        max_value=24,
        value=6
    )
    refresh_rate = st.selectbox(
        "Refresh otomatis setiap:",
        [10, 30, 60],
        index=1
    )

# Koneksi ke MongoDB
@st.cache_resource
def init_mongo():
    client = MongoClient(MONGO_URI)
    db = client.get_database("smart-agriculture")
    return db["air-quality"]

collection = init_mongo()

# Auto-refresh
st.experimental_rerun_interval = refresh_rate * 1000

# Fungsi ambil data
def get_sensor_data(hours):
    time_threshold = datetime.now() - timedelta(hours=hours)
    
    query = {
        "timestamp": {"$gte": time_threshold}
    }
    
    data = list(collection.find(query).sort("timestamp", 1))
    
    # Konversi ke DataFrame
    df = pd.DataFrame(data)
    
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")
    
    return df

# Ambil data
df = get_sensor_data(hours_to_display)

# Tampilkan data terbaru
if not df.empty:
    latest = df.iloc[-1]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🌡 Temperature", f"{latest['temperature']} °C")
    with col2:
        st.metric("💧 Humidity", f"{latest['humidity']} %")
    
    st.divider()
    
    # Buat chart
    tab1, tab2, tab3 = st.tabs(["Line Chart", "Scatter Plot", "Area Chart"])
    
    with tab1:
        fig = px.line(
            df,
            x="timestamp",
            y=["temperature", "humidity"],
            title="Temperature & Humidity Trend",
            labels={"value": "Measurement", "variable": "Parameter"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.scatter(
            df,
            x="temperature",
            y="humidity",
            color="timestamp",
            title="Temperature vs Humidity"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        fig = px.area(
            df,
            x="timestamp",
            y=["temperature", "humidity"],
            title="Temperature & Humidity Area Chart",
            labels={"value": "Measurement", "variable": "Parameter"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # Tabel data mentah
    st.subheader("📄 Raw Data")
    st.dataframe(df[["timestamp", "temperature", "humidity"]])
    
    st.divider()

    # Prediksi & Rekomendasi Penyiraman
    st.subheader("🧠 Prediksi & Rekomendasi Penyiraman Tanaman")

    def rekomendasi_penyiraman(df):
        if len(df) < 2:
            return None, "Data tidak cukup untuk prediksi."

        # Konversi waktu ke detik sebagai fitur numerik
        df["time_seconds"] = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds()

        X = df[["time_seconds"]]
        y = df["humidity"]

        model = LinearRegression()
        model.fit(X, y)

        # Prediksi kelembapan untuk 1 jam ke depan
        next_time = df["time_seconds"].max() + 3600  # 1 jam = 3600 detik
        predicted_humidity = model.predict([[next_time]])[0]

        # Rekomendasi penyiraman
        rekomendasi = "✅ Tidak perlu disiram"
        if predicted_humidity < 40:
            rekomendasi = "🚿 Siram tanaman dalam 1 jam ke depan!"

        return round(predicted_humidity, 2), rekomendasi

    pred_humidity, rekomendasi = rekomendasi_penyiraman(df)

    if pred_humidity is not None:
        st.metric("🔮 Prediksi Kelembapan (1 jam lagi)", f"{pred_humidity} %")
        st.success(rekomendasi if "Tidak perlu" in rekomendasi else rekomendasi)
    else:
        st.info(rekomendasi)

else:
    st.warning("⚠ Tidak ada data yang ditemukan!")

# Judul Aplikasi
st.title("🗣 Chatbot Gemini 1.5")

# Inisialisasi chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pengguna
if prompt := st.chat_input("Apa yang ingin kamu tanyakan?"):
    # Simpan dan tampilkan pesan user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Dapatkan respons dari Gemini
    response = getRespon(prompt)
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Catatan kaki
st.caption("Terakhir diperbarui: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))