import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import os
from streamlit_js_eval import get_geolocation

# ১. পেজ সেটআপ
st.set_page_config(page_title="বিরিয়ানি দিবে?", page_icon="🍗", layout="wide")

CSV_FILE = 'mosque_data.csv'

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if 'real' not in df.columns: df['real'] = 0
        if 'fake' not in df.columns: df['fake'] = 0
        return df
    return pd.DataFrame(columns=['name', 'lat', 'lon', 'menu', 'type', 'district', 'real', 'fake'])

df = load_data()

# ২. সেশন স্টেট (স্মুথ ট্র্যাকিং এবং বাংলাদেশ ভিউ নিশ্চিত করতে)
if 'selected_mosque' not in st.session_state:
    st.session_state.selected_mosque = None
if 'lat' not in st.session_state: st.session_state.lat = 23.6844  # বাংলাদেশের কেন্দ্র
if 'lon' not in st.session_state: st.session_state.lon = 90.3519  # বাংলাদেশের কেন্দ্র
if 'zoom' not in st.session_state: st.session_state.zoom = 7
if 'map_key' not in st.session_state: st.session_state.map_key = 0 # ডাইনামিক ম্যাপ রিফ্রেশার

# ৩. মেইন হেডার
st.markdown("<h2 style='text-align: center; color: #E63946; margin-bottom: 0;'>🍗 রমজানের সেরা বিরিয়ানি ট্র্যাকার 🌙</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 বিরিয়ানি খুঁজুন", "➕ নতুন স্পট যোগ করুন"])

# --- TAB 1: বিরিয়ানি খোঁজা ---
with tab1:
    st.subheader("📍 বিরিয়ানি ম্যাপ")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=st.session_state.zoom)

    for index, row in df.iterrows():
        icon_color = "green" if row['type'] == "Biriyani" else "blue"
        popup_html = f"""
        <div style="text-align: center; font-family: sans-serif; min-width: 150px;">
            <b style="font-size: 15px; color: #E63946;">{row['name']}</b><br>
            <span style="font-size: 12px; color: #555;">📍 {row['district']}</span><br>
            <span style="font-size: 13px;">🍴 {row['menu']}</span><br>
            <hr style="margin: 5px 0;">
            <div style="font-size: 12px; font-weight: bold;">
                ✅ আসল: {row['real']} | ❌ ভুয়া: {row['fake']}
            </div>
        </div>
        """
        
        folium.Marker(
            [row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=180),
            tooltip=row['name'],
            icon=folium.Icon(color=icon_color, icon="cutlery", prefix='fa')
        ).add_to(m)

    map_data = st_folium(m, width="100%", height=450, key="discovery_map")

    if map_data.get("last_object_clicked_tooltip"):
        clicked_name = map_data["last_object_clicked_tooltip"]
        if clicked_name != st.session_state.selected_mosque:
            st.session_state.selected_mosque = clicked_name
            st.rerun()

    if st.session_state.selected_mosque:
        st.write("---")
        st.markdown(f"### 🗳️ আপনি কি **{st.session_state.selected_mosque}**-এ বিরিয়ানি পেয়েছেন?")
        idx = df[df['name'] == st.session_state.selected_mosque].index[0]
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ আসল: {df.at[idx, 'real']}", use_container_width=True):
                df.at[idx, 'real'] += 1
                df.to_csv(CSV_FILE, index=False)
                st.toast("ইতিহাস আপনাকে মনে রাখবে! 😉")
                st.rerun()
        with col2:
            if st.button(f"❌ ভুয়া: {df.at[idx, 'fake']}", use_container_width=True):
                df.at[idx, 'fake'] += 1
                df.to_csv(CSV_FILE, index=False)
                st.toast("মানুষকে বাঁচানোর জন্য ধন্যবাদ! 🛑")
                st.rerun()
    else:
        st.info("💡 কোনো একটি মসজিদের পিনে (Marker) ক্লিক করুন ভোট দেওয়ার জন্য!")



# --- TAB 2: ফানি মোড ও ফ্লোটিং টার্গেট (Fixed CSS) ---
with tab2:
    st.markdown("### ➕ নতুন স্পট যোগ করুন")
    st.write("🎯 ম্যাপের মাঝখানের **'Mosjid'** চিহ্নের নিচে সঠিক জায়গাটি আনুন এবং সেখানে ক্লিক করুন।")
    
    # জিপিএস বাটন
    if st.button("📡 আমার এখনকার লোকেশন ধরো!", use_container_width=True):
        loc = get_geolocation()
        if loc:
            st.session_state.lat = loc['coords']['latitude']
            st.session_state.lon = loc['coords']['longitude']
            st.session_state.zoom = 15 
            st.rerun()

    # ১. CSS: যা ফ্লোটিং টার্গেটকে ম্যাপের ভেতর আটকে রাখবে
    st.markdown("""
        <style>
        /* ম্যাপের কন্টেইনার সেটআপ */
        [data-testid="stVerticalBlock"] > div:has(iframe) {
            position: relative;
        }
        
        /* ফ্লোটিং টার্গেট যা ম্যাপের ঠিক মাঝখানে ভাসবে */
        .mosjid-crosshair {
            position: absolute;
            top: 10%;
            left: 50%;
            transform: translate(-50%, -400%);
            z-index: 9999;
            pointer-events: none;
            text-align: center;
        }
        .mosjid-label {
            background: rgba(230, 57, 70, 0.9);
            color: white;
            font-weight: bold;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            white-space: nowrap;
        }
        </style>
    """, unsafe_allow_html=True)

    # ২. ম্যাপ রেন্ডারিং
    # শুরুতে পয়েন্টার থাকবে কি না তা চেক করার জন্য একটি ফ্ল্যাগ ব্যবহার করছি
    m_input = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=st.session_state.zoom)
    
    # সেশন স্টেটে যদি আগে ক্লিক করা হয়ে থাকে তবেই মার্কার দেখাবে
    if 'has_clicked' in st.session_state and st.session_state.has_clicked:
        folium.Marker(
            [st.session_state.lat, st.session_state.lon], 
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m_input)

    # ম্যাপ ডিসপ্লে
    map_input_data = st_folium(m_input, width="100%", height=400, key="mosque_v_fixed")

    # ফ্লোটিং এলিমেন্টটি ম্যাপের ওপরে ইনজেক্ট করা
    st.markdown("""
        <div class="mosjid-crosshair">
            <div style="font-size: 25px;">🎯</div>
            <div class="mosjid-label">Mosjid</div>
        </div>
    """, unsafe_allow_html=True)

    # ৩. ক্লিক লজিক: ক্লিক করলেই পয়েন্টার আসবে
    if map_input_data and map_input_data.get("last_clicked"):
        new_lat = map_input_data["last_clicked"]["lat"]
        new_lng = map_input_data["last_clicked"]["lng"]
        
        # প্রথমবার ক্লিক করলে বা লোকেশন পরিবর্তন করলে
        if 'has_clicked' not in st.session_state or abs(new_lat - st.session_state.lat) > 0.0001:
            st.session_state.lat = new_lat
            st.session_state.lon = new_lng
            st.session_state.has_clicked = True # এখন পয়েন্টার দেখাবে
            st.rerun()

    # ৪. ফানি ফর্ম সেকশন (আপনার অরিজিনাল ফরম্যাট + এক্সট্রা ফান)
    with st.form("mobile_add_form", clear_on_submit=True):
        if st.session_state.get('has_clicked'):
            st.markdown(f"📍 **নির্বাচিত লোকেশন:** `{st.session_state.lat:.5f}, {st.session_state.lon:.5f}`")
        else:
            st.warning("⚠️ ম্যাপের কোথাও ক্লিক করে আগে বিরিয়ানির জায়গাটি নিশ্চিত করুন!")
            
        new_name = st.text_input("🕌 মসজিদের নাম", placeholder="যেমন: বিরিয়ানি তকদির মসজিদ")
        new_dist = st.text_input("📍 জেলা/মহল্লা", placeholder="যেমন: গুলশান, ঢাকা")
        
        # আপনার হারানো স্পেশাল মেনু সেকশন
        new_menu = st.selectbox("🍱 স্পেশাল মেনু কী দিচ্ছে?", [
            "কাচ্চি বিরিয়ানি (একদম মাখন) 🍗", 
            "শাহী তেহারি (পুরান ঢাকার আসল ঘ্রাণ) 🍚", 
            "খিচুড়ি উৎসব (ডিমসহ মারাত্মক) 🥘", 
            "অন্যান্য স্পেশাল আইটেম 🍲"
        ])
        
        helper_name = st.text_input("👑 আপনার নাম (বিরিয়ানি বীর)")
        
        # আরও কিছু ফানি টেক্সট যোগ করা হলো
        st.write("---")
        funny_quotes = [
            "আপনিই কি সেই আসল বিরিয়ানি খোর? 🍗",
            "বিরিয়ানি বীরের তথ্য দিয়ে জাতিকে উদ্ধার করুন! 🌙",
            "বিরিয়ানি না পাইলেও সওয়াব কিন্তু মিস নাই! 😉",
            "আপনার দেওয়া তথ্যে হাজারো পেট শান্তি পাবে! 🚀"
        ]
        import random
        st.info(random.choice(funny_quotes))

        if st.form_submit_button("ম্যাপে যোগ করুন! 🚀 (জনকল্যাণে)"):
            if new_name and helper_name and st.session_state.get('has_clicked'):
                # ডাটা সেভ লজিক
                new_entry = {
                    "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                    "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", 
                    "type": "Biriyani", "district": new_dist,
                    "real": 0, "fake": 0
                }
                pd.concat([load_data(), pd.DataFrame([new_entry])], ignore_index=True).to_csv(CSV_FILE, index=False)
                st.balloons()
                st.success(f"মাশাআল্লাহ বিরিয়ানি বীর {helper_name}! আপনার সওয়াব কনফার্ম! 😉")
                st.rerun()
            else:
                st.error("সবগুলো ঘর পূরণ করুন এবং ম্যাপে ক্লিক করুন! 🛑")

st.write("---")
st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)
