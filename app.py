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

# ২৩ নম্বর লাইনের পর এই মানগুলো পরিবর্তন করুন
# ২. সেশন স্টেট (এটি যোগ করুন এরর ঠিক করতে)
if 'selected_mosque' not in st.session_state:
    st.session_state.selected_mosque = None
if 'lat' not in st.session_state: st.session_state.lat = 23.6844  # বাংলাদেশের কেন্দ্র
if 'lon' not in st.session_state: st.session_state.lon = 90.3519  # বাংলাদেশের কেন্দ্র
if 'zoom' not in st.session_state: st.session_state.zoom = 8      # পুরো বাংলাদেশ দেখার জন্য জুম ৭

# ৩. মেইন হেডার
st.markdown("<h2 style='text-align: center; color: #E63946; margin-bottom: 0;'>🍗 রমজানের সেরা বিরিয়ানি ট্র্যাকার 🌙</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 বিরিয়ানি খুঁজুন", "➕ নতুন স্পট যোগ করুন"])

# --- TAB 1: বিরিয়ানি খোঁজা ---
with tab1:
    st.subheader("📍 বিরিয়ানি ম্যাপ")
    # ৩০ নম্বর লাইনের আশেপাশে এই পরিবর্তনটি করুন
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
                ✅ আসল: {row['real']} | ❌ ভুয়া: {row['fake']}
            </div>
        </div>
        """
        
        folium.Marker(
            [row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=180),
            tooltip=row['name'],
            icon=folium.Icon(color=icon_color, icon="cutlery", prefix='fa')
        ).add_to(m)

    # ম্যাপ রেন্ডার
    map_data = st_folium(m, width="100%", height=450, key="discovery_map")

    # ম্যাপে ক্লিক করলে নাম সেভ হবে
    if map_data.get("last_object_clicked_tooltip"):
        clicked_name = map_data["last_object_clicked_tooltip"]
        if clicked_name != st.session_state.selected_mosque:
            st.session_state.selected_mosque = clicked_name
            st.rerun()

    # ৪. ভোট দেওয়ার ইন্টারফেস (কোনো ড্রপডাউন নেই, শুধু সিলেক্টেড নাম দেখাবে)
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
        st.info("💡 কোনো একটি মসজিদের পিনে (Marker) ক্লিক করুন ভোট দেওয়ার জন্য!")

# --- TAB 2: নতুন লোকেশন যোগ করা (ডাইনামিক ও আরও ফানি) ---
with tab2:
    st.markdown("### ➕ নতুন স্পট যোগ করুন")
    st.write("নিচের ম্যাপটি নাড়াচাড়া করে মসজিদের ওপর লাল প্লাস (+) চিহ্নটি আনুন।")
    
    if st.button("📡 আমার এখনকার লোকেশন ধরো!", use_container_width=True):
        loc = get_geolocation()
        if loc:
            st.session_state.lat, st.session_state.lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.session_state.zoom = 15 
            st.toast("আপনার এলাকা জিপিএস দিয়ে খুঁজে পেয়েছি! 🎯")
            st.rerun()

    # ১. ম্যাপ তৈরি ও ডাইনামিক সেন্টার মার্কার
    m_input = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=st.session_state.zoom)
    
    # ম্যাপের মাঝখানে একটি স্থির লক্ষ্যবিন্দু (Crosshair)
    folium.Marker(
        [st.session_state.lat, st.session_state.lon], 
        icon=folium.Icon(color='red', icon='plus', prefix='fa'),
        tooltip="এই পয়েন্টটি সেভ হবে"
    ).add_to(m_input)
    
    map_input_data = st_folium(m_input, width="100%", height=300, key="input_map")
    
    # ২. ডাইনামিক ট্র্যাকিং লজিক
    if map_input_data and map_input_data.get("center"):
        new_lat = map_input_data["center"]["lat"]
        new_lon = map_input_data["center"]["lng"]
        
        # লোকেশন পরিবর্তন হলে সেশন স্টেটে আপডেট হবে
        if abs(new_lat - st.session_state.lat) > 0.0001 or abs(new_lon - st.session_state.lon) > 0.0001:
            st.session_state.lat = new_lat
            st.session_state.lon = new_lon

    # ৩. নতুন ফানি মেসেজসহ ফর্ম
    with st.form("mobile_add_form", clear_on_submit=True):
        st.markdown(f"📍 **বর্তমান সিলেকশন:** `{st.session_state.lat:.4f}, {st.session_state.lon:.4f}`")
        
        new_name = st.text_input("🕌 মসজিদের নাম", placeholder="যেমন: বিরিয়ানি তকদির মসজিদ")
        new_dist = st.text_input("📍 জেলা/মহল্লা", placeholder="যেমন: গুলশান, ঢাকা")
        
        # আরও মজার মেনু অপশন
        new_menu = st.selectbox("🍱 আজকের স্পেশাল মেনু কী?", [
            "কাচ্চি বিরিয়ানি (মাংস বেশি) 🍗", 
            "তেহারি (পুরান ঢাকার আসল স্বাদ) 🍚", 
            "খিচুড়ি (ডিমসহ মারাত্মক) 🥘", 
            "তেলে ভাজা ইফতার (গরম গরম) 🍛", 
            "সারপ্রাইজ মেনু (গিয়ে দেখুন) 🎁"
        ])
        
        helper_name = st.text_input("👑 আপনার নাম (বিরিয়ানি বীর)")
        
        # মজার সাবমিট মেসেজ
        funny_quotes = [
            "বিরিয়ানি বীরের অভাব নেই! 🚀",
            "আপনিই কি সেই বিরিয়ানি খোর? 🍗",
            "তথ্য দিয়ে জাতিকে উদ্ধার করুন! 🌙"
        ]
        st.caption(funny_quotes[index % len(funny_quotes)] if 'index' in locals() else funny_quotes[0])

        if st.form_submit_button("ম্যাপে যোগ করুন! 🚀 (জনকল্যাণে)", use_container_width=True):
            if new_name and helper_name:
                new_type = "Biriyani" if any(x in new_menu for x in ["বিরিয়ানি", "তেহারি"]) else "Iftar"
                new_entry = {
                    "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                    "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", "type": new_type, "district": new_dist,
                    "real": 0, "fake": 0
                }
                pd.concat([load_data(), pd.DataFrame([new_entry])], ignore_index=True).to_csv(CSV_FILE, index=False)
                st.balloons()
                st.success(f"মাশাআল্লাহ {helper_name}! আপনার তথ্য সেভ হয়েছে। সওয়াব আর বিরিয়ানি দুইটাই আপনার হোক! 😉")
                st.rerun()
            else:
                st.error("মসজিদ আর আপনার নাম না দিলে কি বিরিয়ানি মিলবে? দয়া করে নাম লিখুন! 🛑")

st.write("---")
st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)
