import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import ee
import geemap.foliumap as geemap 

# ══════════════════════════════════════════
# 1. INISIALISASI GOOGLE EARTH ENGINE
# ══════════════════════════════════════════
try:
    ee.Initialize(project='fabled-archive-491907-g3')
    gee_ready = True
except Exception as e:
    gee_ready = False

# ══════════════════════════════════════════
# 2. KONFIGURASI HALAMAN
# ══════════════════════════════════════════
st.set_page_config(page_title="E-BRIX Dashboard", page_icon="🍃", layout="wide")

# ══════════════════════════════════════════
# 3. INJEKSI CSS CUSTOM
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background-color: #F0F4F1 !important; }
section[data-testid="stSidebar"] { background-color: #1C3829 !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.75) !important; }
section[data-testid="stSidebar"] h1, h2, h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
section[data-testid="stSidebar"] label { color: rgba(255,255,255,0.5) !important; font-size: 10px !important; font-weight: 700 !important; text-transform: uppercase; }
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child { background-color: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; }
section[data-testid="stSidebar"] [data-baseweb="tag"] { background-color: #00b050 !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #ffffff !important; }
section[data-testid="stSidebar"] input[type="text"] { background-color: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; color: #ffffff !important; }
header[data-testid="stHeader"] { background-color: #ffffff !important; border-bottom: 1px solid rgba(0,0,0,0.07) !important; }
.block-container { padding: 1.5rem 1.75rem !important; max-width: 100% !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background-color: #ffffff !important; border: 1px solid rgba(0,0,0,0.07) !important; border-radius: 14px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important; }
[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid rgba(0,0,0,0.07); border-radius: 12px; padding: 0.9rem 1.1rem; border-left: 3px solid #00b050; }
[data-testid="stMetricLabel"] { font-size: 0.7rem !important; color: #7a9a84 !important; font-weight: 600 !important; text-transform: uppercase; }
[data-testid="stMetricValue"] { font-size: 1.55rem !important; font-weight: 800 !important; color: #1a2e20 !important; }
h1, h2, h3 { color: #1a2e20 !important; }
h3 { font-size: 0.88rem !important; font-weight: 700 !important; }
div[role="radiogroup"] > label { margin-bottom: 10px; padding: 5px; font-size: 14px !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 4. LOAD DATA LOKAL
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv("Data_eBrix_Update_Rendah.csv", sep=",", decimal=".")
    df = df.dropna(subset=['Latitude', 'Longitude', 'Nilai_Brix'])
    if 'Tanggal' in df.columns:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    return df

df_raw = load_data()

# ══════════════════════════════════════════
# 5. SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:0 0.5rem 0.5rem;">
        <div style="width:38px;height:38px;background:#00b050;border-radius:10px; display:flex;align-items:center;justify-content:center;">
            <b style="color:white; font-size:18px;">EB</b>
        </div>
        <div>
            <div style="color:#fff;font-size:17px;font-weight:800;">E-BRIX</div>
            <div style="color:rgba(255,255,255,.38);font-size:10px;">Sistem Monitoring Tebu</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    menu_pilihan = st.radio("Pilih Menu", options=["🟢 Dashboard Peta", "📊 Analisis Data"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p style="color:rgba(255,255,255,.3);font-size:9px;font-weight:700;">🔎 FILTER DATA</p>', unsafe_allow_html=True)
    
    semua_blok = sorted(df_raw['Kode_Blok'].dropna().unique().tolist()) if 'Kode_Blok' in df_raw.columns else []
    blok_dipilih = st.multiselect("Blok Lahan", options=semua_blok, default=[])
    
    if 'Tanggal' in df_raw.columns:
        tgl_min = df_raw['Tanggal'].min().date()
        tgl_max = df_raw['Tanggal'].max().date()

        tgl_awal = st.date_input(
            "Dari Tanggal",
            value=tgl_min,
        )
        tgl_akhir = st.date_input(
            "Sampai Tanggal",
            value=tgl_max,
        )

        st.markdown(
            f'<p style="color:rgba(255,255,255,.35);font-size:9px;margin-top:-6px;">'
            f'📅 Data tersedia: {tgl_min.strftime("%d %b %Y")} – {tgl_max.strftime("%d %b %Y")}</p>',
            unsafe_allow_html=True
        )
    else:
        tgl_awal, tgl_akhir, tgl_min, tgl_max = None, None, None, None

    if st.button("✕  Reset Filter", use_container_width=True): st.rerun()

# ══════════════════════════════════════════
# 6. FILTER LOKAL
# ══════════════════════════════════════════
df = df_raw.copy()
filter_blok_aktif = len(blok_dipilih) > 0
if filter_blok_aktif: df = df[df['Kode_Blok'].isin(blok_dipilih)]
if tgl_awal and tgl_akhir and 'Tanggal' in df.columns:
    df = df[(df['Tanggal'].dt.date >= tgl_awal) & (df['Tanggal'].dt.date <= tgl_akhir)]

# ══════════════════════════════════════════
# 7. HEADER & METRIK
# ══════════════════════════════════════════
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center; background:#fff;border-radius:12px;padding:14px 20px; border:1px solid rgba(0,0,0,0.07); margin-bottom:1rem;">
    <div>
        <h2 style="margin:0;font-size:1.05rem;font-weight:800;color:#1a2e20;">Dashboard Monitoring Brix</h2>
        <p style="margin:2px 0 0;font-size:10.5px;color:#7a9a84;">Musim Tanam 2026 &nbsp;·&nbsp; Diperbarui: hari ini</p>
    </div>
    <span style="background:#e6f7ed;color:#1a7a40;font-size:10.5px;font-weight:700; padding:4px 12px;border-radius:20px;">● Sistem Aktif</span>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ Tidak ada data yang cocok dengan filter.")
    st.stop()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Rata-rata Brix", f"{round(df['Nilai_Brix'].mean(), 1)}°")
col_m2.metric("Blok Ditampilkan", df['Kode_Blok'].nunique() if 'Kode_Blok' in df.columns else "–")
col_m3.metric("Brix Tertinggi", f"{round(df['Nilai_Brix'].max(), 1)}°")
col_m4.metric("Brix Terendah", f"{round(df['Nilai_Brix'].min(), 1)}°")
st.markdown("<div style='margin-bottom:0.9rem'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 8. KONTEN UTAMA
# ══════════════════════════════════════════
if menu_pilihan == "🟢 Dashboard Peta":
    with st.container(border=True):
        st.subheader("🗺️ Peta Kemanisan Tebu")

        if gee_ready:
            m = geemap.Map(plugin_Draw=False)
            m.add_basemap('SATELLITE')

            try:
                # 1. PANGGIL ASSET GEE
                asset_id = 'projects/fabled-archive-491907-g3/assets/Data_eBrix_Update_Rendah'
                fc_raw = ee.FeatureCollection(asset_id)

                # 2. PAKSA BACA KOORDINAT 
                def set_geometry(feat):
                    lon = ee.Number(feat.get('Longitude'))
                    lat = ee.Number(feat.get('Latitude'))
                    return ee.Feature(ee.Geometry.Point([lon, lat]), feat.toDictionary())
                
                fc_sensor = fc_raw.map(set_geometry)

                if filter_blok_aktif:
                    fc_sensor = fc_sensor.filter(ee.Filter.inList('Kode_Blok', ee.List(blok_dipilih)))

                m.centerObject(fc_sensor, 16)

                # ==============================================================
                # KUNCI RAHASIA 1: BENTUK BATAS LAHAN (POLIGON LURUS)
                # ==============================================================
                # Membuang efek gelembung (buffer 200). 
                # Menggunakan convexHull untuk menarik garis lurus menutupi area sensor.
                batas_lahan = fc_sensor.geometry().convexHull().buffer(50)

                # ==============================================================
                #: RUMUS GAUSSIAN DENGAN JANGKAUAN LUAS
                # ==============================================================
                kriged_raster = fc_sensor.kriging(
                    propertyName='Nilai_Brix',
                    shape='gaussian',  
                    range=800,         # : Dinaikkan jadi 800 meter agar warna padat menyatu!
                    sill=5.0,         
                    nugget=0.1,
                    maxDistance=2000   
                ).clip(batas_lahan)    #  Hasilnya digunting rapi mengikuti garis lurus batas lahan

                # ==============================================================
                # KUNCI RAHASIA 3: OPASITAS AGAR TIDAK MENYALA (NGEJRENG)
                # ==============================================================
                brix_vis = {
                    'min': 14.0, 
                    'max': 19.0, 
                    'palette': ['#2ecc71', '#f39c12', '#e74c3c'],
                    'opacity': 0.65  # <-- Menambahkan efek kaca/transparan 65%
                }

                m.addLayer(kriged_raster, brix_vis, 'Heatmap Kriging Smooth')
                m.addLayer(fc_sensor, {'color': 'white'}, 'Sensor IoT')

            except Exception as e:
                st.error(f"Gagal memuat Data dari GEE Cloud. Error: {e}")

            if filter_blok_aktif and 'Kode_Blok' in df.columns:
                df_marker = df.groupby('Kode_Blok').agg(lat=('Latitude','mean'), lon=('Longitude','mean'), brix=('Nilai_Brix','mean')).reset_index()
                for _, row in df_marker.iterrows():
                    folium.CircleMarker(
                        location=[row['lat'], row['lon']], radius=10, color='white', weight=2, fill=True, fill_color='#00b050', fill_opacity=0.85,
                        popup=folium.Popup(f"<b>{row['Kode_Blok']}</b><br>Rata-rata: {row['brix']:.1f}°", max_width=150)
                    ).add_to(m)

            legend_html = '''
            <div style="position: fixed; bottom: 20px; right: 20px; width: 140px; height: 120px; background-color: white; z-index:9999; font-size:12px; font-weight:bold; border-radius: 8px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                <div style="margin-bottom:8px; color:#333;">Prediksi Kemanisan:</div>
                <div style="margin-bottom:5px;"><span style="color:#e74c3c; font-size:16px;">■</span> Tinggi (>19%)</div>
                <div style="margin-bottom:5px;"><span style="color:#f39c12; font-size:16px;">■</span> Sedang</div>
                <div><span style="color:#2ecc71; font-size:16px;">■</span> Rendah (<14%)</div>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            st_folium(m, use_container_width=True, height=590, returned_objects=[])
        else:
            st.error("⚠️ Autentikasi Google Earth Engine Belum Selesai!")

elif menu_pilihan == "📊 Analisis Data":
    plotly_base = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=240, xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False), yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False))
    col_kiri, col_kanan = st.columns(2)
    with col_kiri:
        with st.container(border=True):
            st.subheader("📈 Tren Kenaikan Brix")
            if 'Tanggal' in df.columns:
                df_trend = df.groupby('Tanggal')['Nilai_Brix'].mean().reset_index()
                fig_trend = px.line(df_trend, x='Tanggal', y='Nilai_Brix', markers=True, color_discrete_sequence=['#00b050'], labels={'Nilai_Brix': 'Brix (°)', 'Tanggal': ''})
                fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=6), fill='tozeroy', fillcolor='rgba(0,176,80,0.08)')
                fig_trend.update_layout(**plotly_base, hovermode='x unified')
                st.plotly_chart(fig_trend, use_container_width=True)
    with col_kanan:
        with st.container(border=True):
            st.subheader("📊 Status Blok Lahan")
            if 'Kode_Blok' in df.columns:
                df_status = df.groupby('Kode_Blok')['Nilai_Brix'].mean().reset_index().sort_values('Nilai_Brix', ascending=False)
                fig_bar = px.bar(df_status, x='Kode_Blok', y='Nilai_Brix', color='Nilai_Brix', color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c'], text_auto='.1f')
                fig_bar.update_traces(textfont_size=10, textposition='outside', marker_line_width=0)
                fig_bar.update_layout(**plotly_base, coloraxis_showscale=False, bargap=0.25)
                fig_bar.update_xaxes(showgrid=False, zeroline=False)
                st.plotly_chart(fig_bar, use_container_width=True)