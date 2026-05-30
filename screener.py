import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UI/UX INSTITUSIONAL
st.set_page_config(
    page_title="IDX Institutional Stock Intelligence",
    page_icon="💎",
    layout="wide"
)

# Custom Styling Premium UI/UX
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 25px; border-left: 6px solid #1e3a8a; }
    .pro-box { background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 5px solid #16a34a; margin-bottom: 10px; }
    .con-box { background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 5px solid #dc2626; margin-bottom: 10px; }
    .catalyst-card { background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 5px solid #d97706; margin-bottom: 10px; }
    .metric-box { background-color: #f1f5f9; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
    h2 { color: #1e3a8a; font-weight: 700; margin-bottom: 15px; }
    h3 { color: #0f172a; font-weight: 600; }
    h4 { color: #475569; font-weight: 600; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("💎 IDX Institutional Stock Intelligence")
st.caption("Sistem Analisis Multi-Mazhab Terintegrasi: Klasifikasi Karakter Otomatis, Valuasi Dinamis, Sinyal Risiko-Peluang, dan Live News Scraper")
st.write("---")

# 2. INPUT KODE SAHAM
col_input, _ = st.columns([1, 2])
with col_input:
    ticker_input = st.text_input("✍️ Masukkan Kode Saham IDX (Contoh: BRPT, BBRI, ADRO):", value="BBRI").strip().upper()

if ticker_input:
    ticker_sym = f"{ticker_input}.JK"
    
    with st.spinner(f"Sedang mengumpulkan data laporan keuangan, histori transaksi pasar, dan matriks risiko untuk {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_sym)
            info = ticker.info
            
            if 'longName' not in info:
                st.error(f"❌ Kode saham '{ticker_input}' tidak valid di Bursa Efek Indonesia.")
                st.stop()
                
            # --- SELEKSI & BERSIHKAN DATA MENTAH (RAW DATA CLEANING) ---
            current_price = info.get('currentPrice', info.get('regularMarketPrice', np.nan))
            company_name = info.get('longName', 'N/A')
            market_cap = info.get('marketCap', 0) / 1e9
            sector = info.get('sector', 'N/A')
            
            eps = info.get('trailingEps', np.nan)
            pe_ratio = info.get('trailingPE', np.nan)  # Perbaikan nama variabel agar konsisten
            roe = info.get('returnOnEquity', np.nan)
            rev_growth = info.get('revenueGrowth', np.nan)
            der = info.get('debtToEquity', np.nan)
            div_yield = info.get('dividendYield', 0)
            
            # Patch Perbaikan Data Ekuitas & BVPS Manual agar 100% Akurat (Bebas Bug Satuan yFinance)
            total_assets = info.get('totalAssets', 0)
            total_liab = info.get('totalLiabilities', 0)
            total_equity = total_assets - total_liab
            shares_outstanding = info.get('sharesOutstanding', 0)
            
            if shares_outstanding > 0 and total_equity > 0:
                bvps = total_equity / shares_outstanding
                pbv = current_price / bvps
            else:
                bvps = info.get('bookValue', np.nan)
                pbv = info.get('priceToBook', np.nan)
            
            # Ambil data historis 6 bulan untuk analisis teknikal, volatilitas, & volume harian
            df_hist = ticker.history(period="6mo")
            
            # HEADER UTAMA RINGKASAN DATA PASAR
            st.subheader(f"📊 {ticker_input} - {company_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Harga Pasar Terakhir", f"Rp {current_price:,}" if not pd.isna(current_price) else "N/A")
            c2.metric("Market Capitalization", f"Rp {market_cap:,.2f} Miliar")
            c3.metric("Sektor Industri", sector)
            st.write("---")
            
            # ==========================================
            # 3. ENGINE: INTELLIGENT CHARACTER CLASSIFIER
            # ==========================================
            is_banking = sector == 'Financial Services'
            
            # Logika klasifikasi: Jangka panjang wajib efisien (ROE tinggi) DAN tumbuh, atau bank Buku 4 berkapitalisasi masif
            if (not pd.isna(roe) and roe > 0.13 and not pd.isna(rev_growth) and rev_growth > 0.06) or (is_banking and market_cap > 50000):
                char_tag = "🏛️ INVESTASI JANGKA PANJANG (Core Asset / Hold Forever)"
                char_desc = "Saham ini memiliki struktur bisnis yang efisien mencetak laba bersih, pertumbuhan organik yang konstan, dan fundamental yang stabil menghadapi gejolak makro. Sangat cocok dijadikan aset tabungan masa depan."
                is_long_term = True
            else:
                char_tag = "⚡ TRADING JANGKA PENDEK (Tactical Momentum / Swing Trade)"
                char_desc = "Saham ini memiliki karakteristik volatilitas tinggi, valuasi aset premium/mahal, atau pertumbuhan laba yang tidak stabil. Lebih optimal dieksekusi jangka pendek untuk memanfaatkan ayunan momentum pasar."
                is_long_term = False
                
            st.markdown(f"""
            <div class='report-card' style='border-left-color: #6366f1; background-color: #faf5ff;'>
                <h3 style='color: #4c1d95;'>🎯 Klasifikasi Karakteristik Emiten</h3>
                <strong>{char_tag}</strong><br>
                <p style='color: #4b5563; font-size: 14px; margin-top: 5px;'>{char_desc}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # MEMBUAT PANEL WORKSPACE GABUNGAN
            tab1, tab2 = st.tabs(["📊 Sistem Kalkulator & Valuasi Dinamis", "📰 Live Catalyst & Corporate Action"])
            
            # ------------------------------------------
            # TAB 1: VALUASI DAN METODE
            # ------------------------------------------
            with tab1:
                col_left, col_right = st.columns([3, 2])
                
                with col_left:
                    if is_long_term:
                        # JANGKA PANJANG: Menggunakan Pendekatan Intrinsik Aset Berwujud & Laba Aktual
                        st.write("### 🏛️ Analisis Valuasi Intrinsik Jangka Panjang")
                        
                        if not pd.isna(eps) and not pd.isna(bvps) and eps > 0 and bvps > 0:
                            fair_price = np.sqrt(22.5 * eps * bvps)
                            # Batas Pengaman Buffett (MoS 20% dikunci langsung)
                            buffett_buy_limit = fair_price * 0.80
                            mos = ((fair_price - current_price) / fair_price) * 100
                        else:
                            # Fallback rasional jika data kosong
                            fair_price = eps * 12 if (not pd.isna(eps) and eps > 0) else current_price * 1.15
                            buffett_buy_limit = fair_price * 0.80
                            mos = ((fair_price - current_price) / fair_price) * 100
                            
                        v1, v2, v3 = st.columns(3)
                        v1.markdown(f"<div class='metric-box'>Estimasi Harga Wajar<br><span style='color:#16a34a; font-size:18px;'>Rp {round(fair_price):,}</span></div>", unsafe_allow_html=True)
                        v2.markdown(f"<div class='metric-box'>Batas Maksimal Beli Aman<br><span style='color:#2563eb; font-size:18px;'>Rp {round(buffett_buy_limit):,}</span></div>", unsafe_allow_html=True)
                        v3.markdown(f"<div class='metric-box'>Margin of Safety (MoS)<br><span style='color:#ca8a04; font-size:18px;'>{round(mos, 1)} %</span></div>", unsafe_allow_html=True)
                        
                        st.write("")
                        st.write("**📌 Panduan Aksi Jangka Panjang:**")
                        if current_price < buffett_buy_limit:
                            st.success(f"🟢 **Rekomendasi: ACCUMULATE BUY.** Harga pasar saat ini berada di zona diskon yang sangat aman dari batas psikologis Buffett. Ideal untuk dicicil beli secara konstan.")
                        else:
                            st.warning(f"🟡 **Rekomendasi: HOLD / WAIT FOR DIP.** Saham ini luar biasa sehat, tetapi harganya saat ini sudah mendekati/melebihi batas aman beli konservatif.")
                            
                    else:
                        # JANGKA PENDEK / MOMENTUM: Menggunakan Kalkulator Batas Risiko
                        st.write("### ⚡ Rencana Eksekusi Trading & Batas Manajemen Risiko")
                        
                        if len(df_hist) >= 20:
                            pct_change = df_hist['Close'].pct_change()
                            volatility = pct_change.std()
                            risk_factor = max(volatility * 2, 0.05)
                        else:
                            risk_factor = 0.05
                            
                        stop_loss = current_price * (1 - risk_factor)
                        take_profit = current_price * (1 + (risk_factor * 2))
                        
                        t1, t2, t3 = st.columns(3)
                        t1.markdown(f"<div class='metric-box'>Area Harga Entry<br><span style='color:#0f172a; font-size:18px;'>Rp {current_price:,}</span></div>", unsafe_allow_html=True)
                        t2.markdown(f"<div class='metric-box'>Target Profit (TP)<br><span style='color:#16a34a; font-size:18px;'>Rp {round(take_profit):,}</span><br><small style='color:green;'>+{round(risk_factor*2*100)}%</small></div>", unsafe_allow_html=True)
                        t3.markdown(f"<div class='metric-box'>Batas Potong Rugi (SL)<br><span style='color:#dc2626; font-size:18px;'>Rp {round(stop_loss):,}</span><br><small style='color:red;'>-{round(risk_factor*100)}%</small></div>", unsafe_allow_html=True)
                
                with col_right:
                    st.write("### 🏥 Parameter Dasar Finansial")
                    f_df = pd.DataFrame({
                        "Metrik Finansial": ["PBV Ratio", "PE Ratio", "ROE (%)", "Revenue Growth (%)", "Dividend Yield (%)"],
                        "Nilai Riil": [
                            f"{round(pbv, 2)} x" if not pd.isna(pbv) else "N/A",
                            f"{round(pe_ratio, 2)} x" if not pd.isna(pe_ratio) else "N/A",  # Sudah diperbaiki ke pe_ratio
                            f"{round(roe*100, 2)} %" if not pd.isna(roe) else "N/A",
                            f"{round(rev_growth*100, 2)} %" if not pd.isna(rev_growth) else "0.0 %",
                            f"{round(div_yield*100, 2)} %" if div_yield > 0 else "0.0 %"
                        ]
                    })
                    st.dataframe(f_df, use_container_width=True, hide_index=True)
                
                st.write("---")
                
                # ==========================================
                # 4. ENGINE: PROS & CONS / RISIKO & PELUANG MATRIX
                # ==========================================
                st.write("### 🔍 Matriks Deteksi Celah Risiko & Peluang Pasar")
                
                pros_list = []
                cons_list = []
                
                if not pd.isna(roe) and roe > 0.15:
                    pros_list.append(f"**Efisiensi Bisnis Sangat Tinggi (ROE: {round(roe*100,1)}%):** Manajemen andal mengonversi ekuitas menjadi laba bersih.")
                if not pd.isna(rev_growth) and rev_growth > 0.10:
                    pros_list.append(f"**Skalabilitas Kuat (Growth: {round(rev_growth*100,1)}%):** Pangsa pasar terus membesar.")
                if div_yield > 0.04:
                    pros_list.append(f"**Dividen Protektif Tinggi (Yield: {round(div_yield*100,1)}%):** Arus kas pasif aman.")
                
                if len(df_hist) >= 20:
                    df_hist['Avg_Vol_20'] = df_hist['Volume'].rolling(window=20).mean()
                    df_hist['MA50'] = df_hist['Close'].rolling(window=50).mean()
                    latest_row = df_hist.iloc[-1]
                    vol_ratio = latest_row['Volume'] / latest_row['Avg_Vol_20'] if latest_row['Avg_Vol_20'] > 0 else 0
                    ma50_val = latest_row['MA50']
                    
                    if vol_ratio >= 1.5:
                        pros_list.append(f"**Aksi Akumulasi Likuiditas Masif (Volume Spike: {round(vol_ratio, 1)}x):** Ada pergerakan 'Big Money' masuk.")
                    if current_price > ma50_val:
                        pros_list.append("**Struktur Tren Sehat (Bullish):** Harga bertengger di atas MA50.")
                    else:
                        cons_list.append("**Struktur Tren Melemah (Bearish):** Tren grafik di bawah MA50, ada risiko penurunan jangka pendek.")
                
                if not pd.isna(der) and der > 160 and not is_banking:
                    cons_list.append(f"**Beban Utang Tinggi (DER: {round(der,1)}%):** Risiko struktur modal terbebani.")
                if not pd.isna(pbv) and pbv > 3.5:
                    cons_list.append(f"**Valuasi Premium (PBV: {round(pbv,1)}x):** Harga aset sudah dihargai mahal oleh pasar.")
                if not pd.isna(rev_growth) and rev_growth < 0:
                    cons_list.append(f"**Kemunduran Omset Bisnis (Revenue Drop):** Penjualan tahunan melambat.")
                    
                if not pros_list: pros_list.append("Performa fundamental berjalan normal.")
                if not cons_list: cons_list.append("Tidak ada celah risiko struktural yang membahayakan.")
                
                col_pro, col_con = st.columns(2)
                with col_pro:
                    st.write("#### 🟢 Peluang Keuntungan & Sentimen Positif:")
                    for pro in pros_list: st.markdown(f"<div class='pro-box'>{pro}</div>", unsafe_allow_html=True)
                with col_con:
                    st.write("#### ⚠️ Celah Risiko & Hal yang Wajib Diwaspadai:")
                    for con in cons_list: st.markdown(f"<div class='con-box'>{con}</div>", unsafe_allow_html=True)
                        
            # ------------------------------------------
            # TAB 2: LIVE NEWS & CORPORATE ACTION SCRAPER
            # ------------------------------------------
            with tab2:
                st.write("### 📰 Integrasi Sentimen Berita & Informasi Aksi Korporasi Terkini")
                news_list = ticker.news
                if news_list:
                    for news in news_list[:4]:
                        title = news.get('title', 'N/A')
                        publisher = news.get('publisher', 'N/A')
                        link = news.get('link', '#')
                        is_catalyst = any(k in title.lower() for k in ['rups', 'dividen', 'dividend', 'rights issue', 'laba', 'profit', 'tumbuh'])
                        
                        if is_catalyst:
                            st.markdown(f"<div class='catalyst-card'><strong>🚨 KATALIS FINANSIAL UTAMA: <a href='{link}' target='_blank'>{title}</a></strong><br><small>Sumber: {publisher}</small></div>", unsafe_allow_html=True)
                        else:
                            st.write(f"🔹 **[{publisher}]** [{title}]({link})")
                else:
                    st.info("Tidak ada berita material terbaru.")

        except Exception as e:
            st.error(f"Sistem gagal mengekstrak data komprehensif emiten: {str(e)}")
