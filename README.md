# 🍃 e-Brix: Sistem Monitoring & Prediksi Kemanisan Tebu Real-Time

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg)](https://ebrix-dashboard.streamlit.app)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-Powered-blue)](https://earthengine.google.com/)

**e-Brix** adalah platform dashboard manajemen tebu terintegrasi yang menggabungkan teknologi **Internet of Things (IoT)** dan **Geospatial Artificial Intelligence (Geo-AI)**. Sistem ini dirancang untuk memantau dan memprediksi sebaran kadar brix (kemanisan) tebu secara spasial di lahan perkebunan PT PG Rajawali II.

---

## 🚀 Fitur Utama
- **Real-Time Dashboard:** Visualisasi data brix langsung dari sensor IoT.
- **AI Spatial Prediction:** Menggunakan algoritma **Ordinary Kriging** untuk memprediksi kadar brix di area yang tidak memiliki sensor.
- **Dynamic Filtering:** Filter sebaran brix berdasarkan kode blok lahan dan rentang waktu tanam.
- **Enterprise Analytics:** Grafik tren kenaikan brix dan status kesehatan blok menggunakan Plotly.
- **Hybrid Data Source:** Sistem fail-safe yang menghubungkan Cloud Database (PostgreSQL/Supabase) dengan cadangan data lokal (CSV).

---

## 🏗️ Arsitektur Sistem
Sistem ini menggunakan arsitektur *Cloud-to-Dashboard* yang modern:
1. **Data Layer:** Sensor IoT mengirim data ke **PostgreSQL (Supabase)**.
2. **Logic Layer:** **Streamlit (Python)** bertindak sebagai jembatan yang mengambil data dari DB dan menerjemahkannya ke format spasial.
3. **AI Engine:** **Google Earth Engine (GEE)** memproses data titik menjadi hamparan heatmap menggunakan interpolasi Kriging.
4. **Presentation Layer:** Dashboard interaktif yang dapat diakses melalui web browser.

---

## 🧠 Logika Algoritma: Ordinary Kriging
Proyek ini menggunakan metode **Ordinary Kriging** sebagai mesin prediksinya. Logika utamanya adalah:
- **Spatial Autocorrelation:** Mengasumsikan bahwa tebu yang berdekatan memiliki kadar manis yang mirip.
- **Semivariogram Modeling:** Menggunakan model *Gaussian* dengan pengaturan *Range* 800m untuk menghasilkan gradasi warna yang halus (*smooth*).
- **Convex Hull Clipping:** Memotong hasil prediksi secara otomatis mengikuti batas titik sensor terluar agar visualisasi tetap presisi di dalam blok lahan.

---

## 🛠️ Teknologi yang Digunakan
- **Bahasa:** Python, JavaScript (GEE API)
- **Framework:** Streamlit
- **Visualisasi Peta:** Google Earth Engine, Geemap, Folium
- **Analisis Data:** Pandas, Plotly
- **Database:** PostgreSQL (Supabase)

---

## 👨‍💻 Penulis
**Ariz Nur Faishal**

---
