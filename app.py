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



# --- TAB 2: ফ্লোটিং Mosjid এবং ক্লিক-বেসড সিলেকশন ---
with tab2:
    st.markdown("### ➕ নতুন স্পট যোগ করুন")
    st.write("🎯 স্ক্রিনের মাঝখানের চিহ্ন দেখে ম্যাপের সঠিক জায়গায় **ক্লিক করুন** পয়েন্টার সেট করতে।")
    
    # জিপিএস বাটন
    if st.button("📡 আমার এখনকার লোকেশন ধরো!", use_container_width=True):
        loc = get_geolocation()
        if loc:
            st.session_state.lat, st.session_state.lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.session_state.zoom = 15 
            st.rerun()

    # ১. স্ক্রিনের মাঝখানে ভাসমান "Mosjid" চিহ্নের জন্য CSS
    st.markdown("""
        <style>
        .map-wrapper {
            position: relative;
            width: 100%;
        }
        .floating-label {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -100%);
            z-index: 999;
            pointer-events: none; /* যাতে ম্যাপ ক্লিক করতে বাধা না দেয় */
            text-align: center;
            opacity: 0.6; /* ঝাপসা দেখানোর জন্য */
        }
        .mosjid-text {
            font-size: 14px;
            font-weight: bold;
            color: #E63946;
            background: rgba(255, 255, 255, 0.7);
            padding: 2px 5px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ২. ম্যাপ রেন্ডারিং কন্টেইনার
    st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
    
    # ভাসমান চিহ্ন (সব সময় মাঝখানে থাকবে)
    st.markdown('<div class="floating-label"><div style="font-size: 25px;">🎯</div><div class="mosjid-text">Mosjid</div></div>', unsafe_allow_html=True)

    m_input = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=st.session_state.zoom)
    
    # ৩. আসল পয়েন্টার (যেখানে ইউজার ক্লিক করবে সেখানে থাকবে)
    folium.Marker(
        [st.session_state.lat, st.session_state.lon], 
        icon=folium.Icon(color='red', icon='info-sign'),
        tooltip="Selected Mosque Location"
    ).add_to(m_input)
    
    # ম্যাপ ডিসপ্লে
    map_input_data = st_folium(m_input, width="100%", height=400, key="mosque_picker_v3")
    st.markdown('</div>', unsafe_allow_html=True)

    # ৪. ক্লিক করলে পয়েন্টার আপডেট করার লজিক
    if map_input_data and map_input_data.get("last_clicked"):
        clicked_lat = map_input_data["last_clicked"]["lat"]
        clicked_lon = map_input_data["last_clicked"]["lng"]
        
        # যদি ক্লিক করা জায়গা আগের থেকে আলাদা হয়, তবেই আপডেট হবে
        if abs(clicked_lat - st.session_state.lat) > 0.00001 or abs(clicked_lon - st.session_state.lon) > 0.00001:
            st.session_state.lat = clicked_lat
            st.session_state.lon = clicked_lon
            st.rerun()

    # ৫. ডাটা এন্ট্রি ফর্ম
    with st.form("mobile_add_form", clear_on_submit=True):
        st.markdown(f"📍 **সিলেক্টেড লোকেশন:** `{st.session_state.lat:.5f}, {st.session_state.lon:.5f}`")
        
        new_name = st.text_input("🕌 মসজিদের নাম")
        new_dist = st.text_input("📍 জেলা/মহল্লা")
        new_menu = st.selectbox("🍱 স্পেশাল মেনু", ["কাচ্চি বিরিয়ানি 🍗", "শাহী তেহারি 🍚", "খিচুড়ি 🥘", "অন্যান্য"])
        helper_name = st.text_input("👑 আপনার নাম")

        if st.form_submit_button("ম্যাপে যোগ করুন! 🚀", use_container_width=True):
            if new_name and helper_name:
                new_entry = {
                    "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                    "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", "type": "Biriyani", "district": new_dist,
                    "real": 0, "fake": 0
                }
                pd.concat([load_data(), pd.DataFrame([new_entry])], ignore_index=True).to_csv(CSV_FILE, index=False)
                st.balloons()
                st.success("বিরিয়ানি বীর হিসেবে আপনার নাম নথিভুক্ত হলো! 😉")
                st.rerun()

st.write("---")
st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)
