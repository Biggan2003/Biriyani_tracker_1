import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import os
from streamlit_js_eval import get_geolocation

# ১. পেজ সেটআপ
st.set_page_config(page_title="বিরিয়ানি দিবে?", page_icon="🍗", layout="wide")

CSV_FILE = 'mosque_data.csv'

# ২. ডেটা লোড/সেভ ফাংশন
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if 'real' not in df.columns: df['real'] = 0
        if 'fake' not in df.columns: df['fake'] = 0
        return df
    return pd.DataFrame(columns=['name', 'lat', 'lon', 'menu', 'type', 'district', 'real', 'fake'])

def save_data(new_row):
    df = load_data()
    new_row['real'] = 0
    new_row['fake'] = 0
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

df = load_data()

# ৩. ভোট প্রসেসিং (Query Params দিয়ে পপআপের ভেতর থেকে ভোট ধরা)
params = st.query_params
if "vote_idx" in params and "type" in params:
    idx = int(params["vote_idx"])
    v_type = params["type"]
    
    # ভোট আপডেট
    df.at[idx, v_type] += 1
    df.to_csv(CSV_FILE, index=False)
    
    # প্যারামিটার ক্লিয়ার করে পেজ রিফ্রেশ
    st.query_params.clear()
    st.toast("ভোট সফল হয়েছে! 🗳️")
    st.rerun()

# ৪. সেশন স্টেট
if 'lat' not in st.session_state: st.session_state.lat = 23.8103
if 'lon' not in st.session_state: st.session_state.lon = 90.4125

st.markdown("<h2 style='text-align: center; color: #E63946; margin-bottom: 0;'>🍗 রমজানের সেরা বিরিয়ানি ট্র্যাকার 🌙</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 বিরিয়ানি খুঁজুন", "➕ নতুন স্পট যোগ করুন"])

# --- TAB 1: বিরিয়ানি খোঁজা (পপআপের ভেতর ভোট) ---
with tab1:
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=14)

    for index, row in df.iterrows():
        icon_color = "green" if row['type'] == "Biriyani" else "blue"
        gmaps_url = f"https://www.google.com/maps?q={row['lat']},{row['lon']}"
        
        # ভোট দেওয়ার লিঙ্ক (পপআপের ভেতর কাজ করার জন্য)
        real_link = f"/?vote_idx={index}&type=real"
        fake_link = f"/?vote_idx={index}&type=fake"

        # পপআপ ডিজাইন (আপনার স্ক্রিনশটের মতো কিন্তু বাটনসহ)
        popup_html = f"""
        <div style="text-align: center; font-family: sans-serif; min-width: 180px;">
            <b style="font-size: 16px; color: #E63946;">{row['name']}</b><br>
            <span style="font-size: 13px; color: #555;">📍 {row['district']}</span><br>
            <span style="font-size: 13px;">🍴 {row['menu']}</span><br>
            <hr style="margin: 8px 0;">
            
            <div style="margin-bottom: 10px;">
                <a href="{real_link}" target="_self" style="text-decoration: none; padding: 4px 8px; background: #28a745; color: white; border-radius: 3px; font-size: 11px; margin-right: 5px;">✅ আসল: {row['real']}</a>
                <a href="{fake_link}" target="_self" style="text-decoration: none; padding: 4px 8px; background: #dc3545; color: white; border-radius: 3px; font-size: 11px;">❌ ভুয়া: {row['fake']}</a>
            </div>
            
            <a href="{gmaps_url}" target="_blank" style="display: block; padding: 6px; background: #1D3557; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold;">রাস্তা দেখাও 🗺️</a>
        </div>
        """
        
        folium.Marker(
            [row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=icon_color, icon="cutlery", prefix='fa')
        ).add_to(m)

    st_folium(m, width="100%", height=500, key="discovery_map")

# --- TAB 2: নতুন লোকেশন যোগ করা (আগের মতোই) ---
with tab2:
    st.markdown("### ➕ নতুন স্পট যোগ করুন")
    if st.button("📡 আমার লোকেশন ধরো!", use_container_width=True):
        loc = get_geolocation()
        if loc:
            st.session_state.lat = loc['coords']['latitude']
            st.session_state.lon = loc['coords']['longitude']
            st.rerun()

    m_input = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15)
    folium.Marker([st.session_state.lat, st.session_state.lon], icon=folium.Icon(color='red')).add_to(m_input)
    map_input_data = st_folium(m_input, width="100%", height=250, key="input_map")
    
    if map_input_data.get("last_clicked"):
        st.session_state.lat = map_input_data["last_clicked"]["lat"]
        st.session_state.lon = map_input_data["last_clicked"]["lng"]
        st.rerun()

    with st.form("mobile_add_form", clear_on_submit=True):
        new_name = st.text_input("🕌 মসজিদের নাম")
        new_dist = st.text_input("📍 জেলা/মহল্লা")
        new_menu = st.selectbox("🍱 স্পেশাল মেনু কী?", ["কাচ্চি বিরিয়ানি 🍗", "শাহী তেহারি 🍚", "খিচুড়ি উৎসব 🥘", "তেলে ভাজা ইফতার 🍛", "অন্যান্য"])
        helper_name = st.text_input("👑 আপনার নাম")
        
        if st.form_submit_button("ম্যাপে যোগ করুন! 🚀", use_container_width=True):
            if new_name and helper_name:
                new_type = "Biriyani" if any(x in new_menu for x in ["বিরিয়ানি", "তেহারি"]) else "Iftar"
                new_entry = {
                    "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                    "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", "type": new_type, "district": new_dist
                }
                save_data(new_entry)
                st.balloons()
                st.rerun()

st.write("---")
st.markdown(f"<p style='text-align: center; color: gray;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)
