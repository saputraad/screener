import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UI/UX PREMIUM
st.set_page_config(
    page_title="IDX Ultimate Stock Intelligence",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling untuk Laporan Analisis
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 25px; border-left: 6px solid #1e3a8a; }
    .catalyst-card { background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 5px solid #d97706; margin-bottom: 10px; }
    .metric-box { background-color: #f1f5f9; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    h2 { color: #1e3a8a; font-weight: 700; margin-bottom: 15px; }
    h3 { color: #0f172a; font-weight: 600; }
    h4 { color: #475569; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 IDX Ultimate Stock Intelligence")
st.caption("Analisis Harga Wajar, Margin of Safety, Integrasi 4 Metode Multibagger, dan Live Corporate Action")
st.write("---")

# 2. INPUT KODE SAHAM
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_input = st.text_input("✍️ Masukkan Kode Saham IDX (Contoh: ADRO, BBCA, AMRT):", value="BBCA").strip().upper()

if ticker_input:
    ticker_sym = f"{ticker_input}.JK"
    
    with st.spinner(f"Mengekstrak laporan keuangan terbaru dan berita pasar untuk {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info
            
            if 'longName' not in info:
                st.error(f"❌ Kode saham '{ticker_input}' tidak valid di IDX.")
                st.stop()
                
            # Mengambil data harga terakhir & fundamental dasar
            current_price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            company_name = info.get('longName', 'N/A')
            market_cap = info.get('marketCap', 0) / 1e9
            
            # Ekstrak data krusial untuk perhitungan harga wajar
            eps = info.get('trailingEps', np.nan)
            bvps = info.get('bookValue', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            rev_growth = info.get('revenueGrowth', np.nan)
            der = info.get('debtToEquity', np.nan)
            
            # TAMPILAN HEADER RINGKASAN EMITEN
            st.subheader(f"📊 {ticker_input} - {company_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Terakhir", f"Rp {current_price:,}" if not pd.isna(current_price) else "N/A")
            c2.metric("Market Capitalization", f"Rp {market_cap:,.2f} Miliar")
            c3.metric("Sektor Industri", info.get('sector', 'N/A'))
            st.write("---")
            
            # ==========================================
            # MODUL: VALUASI HARGA WAJAR & MARGIN OF SAFETY (MoS)
            # ==========================================
            st.markdown("<div class='report-card' style='border-left-color: #10b981;'>", unsafe_allow_html=True)
            st.markdown("<h2>🎯 Perhitungan Harga Wajar & Margin of Safety (MoS)</h2>", unsafe_allow_html=True)
            
            # Perhitungan Harga Wajar menggunakan Rumus Klasik Graham & Proyeksi Laba Benjamin Graham
            # Rumus Graham Number: Target_Price = sqrt(22.5 * EPS * BVPS)
            if not pd.isna(eps) and not pd.isna(bvps) and eps > 0 and bvps > 0:
                fair_price = np.sqrt(22.5 * eps * bvps)
                mos = ((fair_price - current_price) / fair_price) * 100
            else:
                # Fallback ke metode PE vs Pertumbuhan rata-rata jika data Book Value tidak stabil
                if not pd.isna(eps) and eps > 0:
                    growth_rate = (rev_growth * 100) if (not pd.isna(rev_growth) and rev_growth > 0) else 10
                    fair_price = eps * (8.5 + (2 * growth_rate)) # Rumus Graham Intrinsic Value
                    mos = ((fair_price - current_price) / fair_price) * 100
                else:
                    fair_price = np.nan
                    mos = np.nan
            
            f1, f2, f3 = st.columns(3)
            f1.markdown(f"<div class='metric-box'>Harga Saat Ini<br><span style='color:#0f172a; font-size:20px;'>Rp {current_price:,}</span></div>", unsafe_allow_html=True)
            f2.markdown(f"<div class='metric-box'>Estimasi Harga Wajar<br><span style='color:#10b981; font-size:20px;'>Rp {round(fair_price):,}</span></div>", unsafe_allow_html=True)
            
            if not pd.isna(mos):
                mos_color = "#10b981" if mos > 20 else ("#d97706" if mos >= 0 else "#dc2626")
                f3.markdown(f"<div class='metric-box'>Margin of Safety (MoS)<br><span style='color:{mos_color}; font-size:20px;'>{round(mos, 2)} %</span></div>", unsafe_allow_html=True)
                
                st.markdown("<h4>📌 Penilaian Tingkat Keamanan Diskon (MoS):</h4>", unsafe_allow_html=True)
                if mos > 30:
                    st.success(f"🟢 **SANGAT DISKON (Underpriced):** Harga wajar berada jauh di atas harga pasar saat ini. Tingkat keamanan investasi Anda tinggi karena diskon mencapai {round(mos)}%.")
                elif mos >= 0:
                    st.info(f"🟡 **WAJAR (Fair Value):** Harga pasar saat ini mencerminkan valuasi aslinya. Diskon tipis sebesar {round(mos)}%. Risiko menengah.")
                else:
                    st.error(f"🔴 **KEMAHALAN (Overpriced):** Saham ini diperdagangkan dalam kondisi premium (MoS Minus). Anda membeli di harga yang terlalu tinggi dibanding nilai fundamental internalnya.")
            else:
                f3.markdown("<div class='metric-box'>Margin of Safety (MoS)<br><span style='color:#dc2626; font-size:20px;'>N/A</span></div>", unsafe_allow_html=True)
                st.warning("Data keuangan kuartalan tidak mencukupi untuk memproyeksikan valuasi intrinsik.")
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # AMBIL DATA HISTORIS UNTUK ANALISIS VOLUME & TREND
            df_hist = ticker.history(period="6mo")
            
            # ==========================================
            # METODE 1 & 2: VALUE & GROWTH INVESTING
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>📈 Metode 1 & 2: Value & Growth Deep Analysis</h2>", unsafe_allow_html=True)
            
            pbv = info.get('priceToBook', np.nan)
            pe = info.get('trailingPE', np.nan)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='metric-box'>PBV Ratio<br><span style='color:#2563eb;'>{pbv if not pd.isna(pbv) else 'N/A'} x</span></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-box'>PE Ratio<br><span style='color:#2563eb;'>{pe if not pd.isna(pe) else 'N/A'} x</span></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-box'>ROE<br><span style='color:#16a34a;'>{round(roe*100, 2) if not pd.isna(roe) else 'N/A'} %</span></div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='metric-box'>Revenue Growth<br><span style='color:#16a34a;'>{round(rev_growth*100, 2) if not pd.isna(rev_growth) else '0.0'} %</span></div>", unsafe_allow_html=True)
            
            st.markdown("<h4>🔍 Mengapa Analisis Bisnis Ini Baik/Buruk:</h4>", unsafe_allow_html=True)
            
            # Deteksi kelebihan dan kekurangan fundamental
            pros = []
            cons = []
            
            if not pd.isna(roe) and roe > 0.15: pros.append(f"Efisiensi laba bersih (ROE: {round(roe*100,1)}%) di atas rata-rata industri, manajemen sukses mengelola ekuitas.")
            else: cons.append("Tingkat efisiensi modal rendah, laba bersih kurang optimal dibanding modal pemegang saham.")
            
            if not pd.isna(rev_growth) and rev_growth > 0.08: pros.append(f"Skalabilitas bisnis terbukti kuat dengan pertumbuhan omset tahunan sebesar {round(rev_growth*100,1)}%.")
            else: cons.append("Pertumbuhan pendapatan mandek atau melambat. Sinyal bisnis mulai jenuh (mature).")
            
            if not pd.isna(der) and der < 120: pros.append(f"Rasio utang terkendali dengan aman (DER: {round(der,1)}%), meminimalkan risiko likuidasi atau kebangkrut.")
            else: cons.append(f"Beban utang perusahaan cukup tinggi (DER: {round(der,1)}%), rentan terhadap kenaikan suku bunga makro.")
            
            col_pro, col_con = st.columns(2)
            with col_pro:
                st.write("**✅ Sisi Positif (Kelebihan Fundamental):**")
                for p in pros: st.success(p)
            with col_con:
                st.write("**⚠️ Sisi Negatif (Kelemahan Fundamental):**")
                for c in cons: st.error(c)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            # ==========================================
            # METODE 3 & 4: BANDARMOLOGI & TIMING ENTRY
            # ==========================================
            st.markdown("<div class='report-card'>", unsafe_allow_html=True)
            st.markdown("<h2>⚡ Metode 3 & 4: Proxy Akumulasi & Analisis Tren</h2>", unsafe_allow_html=True)
            
            if len(df_hist) >= 50:
                df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
                df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
                
                latest_row = df_hist.iloc[-1]
                vol_ratio = latest_row['Volume'] / latest_row['Avg_Vol_20'] if latest_row['Avg_Vol_20'] > 0 else 0
                ma50_val = latest_row['MA50']
                
                t1, t2 = st.columns(2)
                t1.markdown(f"<div class='metric-box'>Volume Ratio Hari Ini<br><span style='color:#ca8a04; font-size:20px;'>{round(vol_ratio, 2)} x</span></div>", unsafe_allow_html=True)
                
                trend_status = "🟢 BULLISH (Di Atas MA50)" if current_price > ma50_val else "🔴 BEARISH (Di Bawah MA50)"
                t2.markdown(f"<div class='metric-box'>Status Tren Jangka Menengah<br><span style='color:#0f172a; font-size:18px;'>{trend_status}</span></div>", unsafe_allow_html=True)
                
                st.markdown("<h4>📌 Kesimpulan Strategi Masuk (Timing):</h4>", unsafe_allow_html=True)
                if current_price > ma50_val and vol_ratio >= 1.5:
                    st.success("🎯 **MOMEN EMAS (Strong Entry):** Saham ini sedang berada di jalur akumulasi bandar yang masif dan tren harga terkonfirmasi naik. Probabilitas keberhasilan swing trading sangat tinggi.")
                elif current_price < ma50_val and vol_ratio >= 1.8:
                    st.warning("⚠️ **AKUMULASI DI HARGA BAWAH (Buy on Weakness):** Harga saham sedang turun (*Downtrend*), namun volume transaksi mendadak melonjak tinggi di harga murah. Ini mengindikasikan adanya institusi yang menampung barang secara diam-diam. Silakan masuk dengan metode mencicil perlahan.")
                elif current_price > ma50_val:
                    st.info("🟡 **HOLD & WATCHLIST:** Tren harga sehat, namun pasar sedang sepi transaksi hari ini. Tunggu hingga volume kembali meningkat.")
                else:
                    st.error("🔴 **WAIT AND SEE:** Saham berada di pola penurunan dan sepi peminat. Jangan terburu-buru masuk demi menghindari *floating loss* berkepanjangan.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # ==========================================
            # MODUL LIVE NEWS & CORPORATE ACTION SCRAPER
            # ==========================================
            st.markdown("<h2>📰 Katalis Terkini & Informasi Aksi Korporasi (Live Scraper)</h2>", unsafe_allow_html=True)
            
            news_list = ticker.news
            if news_list:
                for news in news_list[:4]: # Menampilkan 4 berita pasar terbaru terakurat
                    title = news.get('title', 'N/A')
                    publisher = news.get('publisher', 'N/A')
                    link = news.get('link', '#')
                    
                    # Logika pencarian kata kunci otomatis untuk menandai RUPS / Dividen / Right Issue
                    is_catalyst = any(keyword in title.lower() for keyword in ['rups', 'dividen', 'dividend', 'rights issue', 'acquisition', 'laba', 'profit', 'tumbuh'])
                    
                    if is_catalyst:
                        st.markdown(f"""
                        <div class='catalyst-card'>
                            <strong>🚨 KATALIS UTAMA: <a href='{link}' target='_blank'>{title}</a></strong><br>
                            <small>Sumber: {publisher} | Sentimen: Berpotensi Mempengaruhi Harga Saham</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.write(f"🔹 **[{publisher}]** [{title}]({link})")
            else:
                st.info("Tidak ada berita korporat atau pengumuman RUPS terbaru yang terdeteksi dalam sistem pasar terdekat.")
                
        except Exception as e:
            st.error(f"Gagal melakukan pembacaan data komprehensif: {str(e)}")
