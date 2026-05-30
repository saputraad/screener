import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UI/UX
st.set_page_config(
    page_title="IDX Deep Stock Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Custom Styling Premium UI
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #1e3a8a; }
    .metric-box { background-color: #f1f5f9; padding: 10px 15px; border-radius: 8px; text-align: center; font-weight: bold; }
    h2 { color: #1e3a8a; margin-bottom: 15px; }
    h4 { color: #475569; }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 IDX Deep Stock Analyzer")
st.caption("Masukkan Kode Saham untuk Melakukan Analisis Komprehensif Berdasarkan 4 Metode Multibagger")
st.write("---")

# 2. INPUT KODE SAHAM (DENGAN UX YANG MUDAH)
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_input = st.text_input("✍️ Ketik Kode Saham IDX (Contoh: BBCA, ADRO, AMRT):", value="ADRO").strip().upper()

if ticker_input:
    ticker_sym = f"{ticker_input}.JK"
    
    with st.spinner(f"Sedang menarik data akurat untuk {ticker_input} dari pasar..."):
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info
            
            # Cek validitas data terambil
            if 'longName' not in info:
                st.error(f"❌ Kode saham '{ticker_input}' tidak ditemukan atau tidak aktif di IDX. Pastikan kode terdiri dari 4 huruf.")
                st.stop()
                
            # Mengambil data harga terakhir
            current_price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            company_name = info.get('longName', 'N/A')
            market_cap = info.get('marketCap', 0) / 1e9  # Ubah ke Miliar Rp
            
            # TAMPILAN HEADER RINGKASAN EMITEN
            st.subheader(f"📊 {ticker_input} - {company_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Terakhir", f"Rp {current_price:,}" if not pd.isna(current_price) else "N/A")
            c2.metric("Market Capitalization", f"Rp {market_cap:,.2f} Miliar")
            c3.metric("Sektor Industri", info.get('sector', 'N/A'))
            st.write("---")
            
            # AMBIL DATA HISTORIS UNTUK TEKNIKAL & VOLUME (6 Bulan)
            df_hist = ticker.history(period="6mo")
            
            # ==========================================
            # METODE 1: VALUE INVESTING ANALYSIS
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>1. Value Investing (Analisis Valuasi & Aset)</h2>", unsafe_allow_html=True)
            
            pbv = info.get('priceToBook', np.nan)
            pe = info.get('trailingPE', np.nan)
            
            v1, v2, _ = st.columns([1, 1, 2])
            v1.markdown(f"<div class='metric-box'>PBV Ratio<br><span style='color:#2563eb; font-size:20px;'>{pbv if not pd.isna(pbv) else 'N/A'} x</span></div>", unsafe_allow_html=True)
            v2.markdown(f"<div class='metric-box'>PE Ratio<br><span style='color:#2563eb; font-size:20px;'>{pe if not pd.isna(pe) else 'N/A'} x</span></div>", unsafe_allow_html=True)
            
            # Kesimpulan Metode 1
            st.markdown("<h4>📌 Kesimpulan Valuasi:</h4>", unsafe_allow_html=True)
            if not pd.isna(pbv) and not pd.isna(pe):
                if pbv < 1.5 and pe < 10:
                    st.success("🟢 **UNDERVALUED (Murah):** Saham ini tergolong murah secara aset dan laba harian. Memiliki *Margin of Safety* yang sangat aman untuk investasi jangka panjang.")
                elif pbv < 3.0 and pe < 18:
                    st.info("🟡 **FAIR VALUE (Wajar):** Valuasi saham berada di rentang wajar perusahaan bertumbuh. Risiko moderat.")
                else:
                    st.error("🔴 **OVERVALUED (Mahal):** Harga pasar sudah terlampau premium/mahal dibanding nilai buku dan laba bersih aktualnya.")
            else:
                st.warning("Data finansial tidak lengkap untuk menghitung valuasi.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # ==========================================
            # METODE 2: GROWTH INVESTING ANALYSIS
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>2. Growth Investing (Analisis Skalabilitas & Profitabilitas)</h2>", unsafe_allow_html=True)
            
            roe = info.get('returnOnEquity', np.nan)
            rev_growth = info.get('revenueGrowth', np.nan)
            der = info.get('debtToEquity', np.nan)
            
            g1, g2, g3 = st.columns(3)
            g1.markdown(f"<div class='metric-box'>Return on Equity (ROE)<br><span style='color:#16a34a; font-size:20px;'>{round(roe*100, 2) if not pd.isna(roe) else 'N/A'} %</span></div>", unsafe_allow_html=True)
            g2.markdown(f"<div class='metric-box'>Revenue Growth<br><span style='color:#16a34a; font-size:20px;'>{round(rev_growth*100, 2) if not pd.isna(rev_growth) else '0.0'} %</span></div>", unsafe_allow_html=True)
            g3.markdown(f"<div class='metric-box'>Rasio Utang (DER)<br><span style='color:#dc2626; font-size:20px;'>{round(der, 2) if not pd.isna(der) else '0.0'} %</span></div>", unsafe_allow_html=True)
            
            # Kesimpulan Metode 2
            st.markdown("<h4>📌 Kesimpulan Kinerja Bisnis:</h4>", unsafe_allow_html=True)
            if not pd.isna(roe):
                conditions = []
                if roe > 0.15: conditions.append("perusahaan sangat efisien mencetak laba bersih (ROE > 15%)")
                if not pd.isna(rev_growth) and rev_growth > 0.10: conditions.append("pendapatan bisnis bertumbuh sehat (>10%)")
                if not pd.isna(der) and der < 150: conditions.append("tingkat utang aman di bawah batas risiko (<150%)")
                
                if len(conditions) >= 2:
                    st.success(f"🟢 **HIGH GROWTH & STABLE:** Bisnis berjalan sangat impresif karena {', '.join(conditions)}. Memiliki struktur internal yang kuat untuk menjadi raja sektor di masa depan.")
                else:
                    st.warning("🟡 **SLOW/RISKY GROWTH:** Pertumbuhan usaha cenderung melambat atau terbebani oleh rasio utang yang tinggi. Efisiensi modal perlu diperhatikan.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # ==========================================
            # METODE 3: BANDARMOLOGI PROXY (VOLUME SPIKE)
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>3. Proxy Bandarmologi (Analisis Akumulasi Likuiditas)</h2>", unsafe_allow_html=True)
            
            if len(df_hist) >= 20:
                df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
                latest_row = df_hist.iloc[-1]
                
                current_volume = latest_row['Volume']
                avg_vol_20 = latest_row['Avg_Vol_20']
                vol_ratio = current_volume / avg_vol_20 if avg_vol_20 > 0 else 0
                
                b1, _ = st.columns([1, 3])
                b1.markdown(f"<div class='metric-box'>Volume Ratio Hari Ini<br><span style='color:#ca8a04; font-size:20px;'>{round(vol_ratio, 2)} x</span></div>", unsafe_allow_html=True)
                
                st.markdown("<h4>📌 Kesimpulan Deteksi Bandar/Institusi:</h4>", unsafe_allow_html=True)
                if vol_ratio >= 2.0:
                    st.success(f"🟢 **MASSIVE ACCUMULATION:** Terjadi lonjakan volume luar biasa ({round(vol_ratio, 1)}x lipat dari rata-rata). Ini adalah tanda valid bahwa **Big Money / Bandar sedang melakukan pembelian masif**.")
                elif vol_ratio >= 1.3:
                    st.info(f"🟡 **NORMAL ACCUMULATION:** Volume di atas rata-rata harian harian. Ada ketertarikan pasar yang konstan dari institusi keuangan.")
                else:
                    st.error("🔴 **NO ACCUMULATION / SILENT:** Perdagangan sepi dan volume berada di bawah rata-rata. Pihak pengendali pasar (Bandar) sedang tidak menggerakkan saham ini.")
            else:
                st.warning("Data historis tidak mencukupi untuk analisis volume harian.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # ==========================================
            # METODE 4: TECHNICAL & ENTRY POINT TIMING
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>4. Technical Analysis (Penentuan Waktu Entry Tepat)</h2>", unsafe_allow_html=True)
            
            if len(df_hist) >= 50:
                df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
                latest_row = df_hist.iloc[-1]
                ma50_val = latest_row['MA50']
                
                t1, _ = st.columns([1, 3])
                trend_status = "BULLISH (Di Atas MA50)" if current_price > ma50_val else "BEARISH (Di Bawah MA50)"
                trend_color = "#16a34a" if current_price > ma50_val else "#dc2626"
                t1.markdown(f"<div class='metric-box'>Tren Harga Jangka Menengah<br><span style='color:{trend_color}; font-size:18px;'>{trend_status}</span></div>", unsafe_allow_html=True)
                
                st.markdown("<h4>📌 Kesimpulan Momentum Entry:</h4>", unsafe_allow_html=True)
                if current_price > ma50_val and vol_ratio >= 1.5:
                    st.success("🎯 **STRONG ENTRY POINT (Waktu Sempurna):** Saham terkonfirmasi berada di tren naik (*Uptrend*) sekaligus didukung lonjakan volume akumulasi besar. Momen ideal untuk *Buy* demi memaksimalkan keuntungan cepat.")
                elif current_price > ma50_val:
                    st.info("🟡 **HOLD / WAIT FOR BREAKOUT:** Tren utama sudah bagus (*Uptrend*), namun belum ada ledakan volume transaksi hari ini. Disarankan mencicil beli perlahan atau tunggu *breakout volume*.")
                else:
                    st.error("🔴 **AVOID (Jangan Masuk Dulu):** Saham sedang berada di fase *Downtrend*. Walaupun harganya murah, masuk sekarang berisiko membuat modal Anda tertidur lama menunggu pembalikan arah.")
            else:
                st.warning("Data historis harga tidak cukup untuk menghitung Moving Average.")
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
