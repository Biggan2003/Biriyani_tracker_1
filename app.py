import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import os
from streamlit_js_eval import get_geolocation

# ১. পেজ সেটআপ (টাইটেল এবং আইকন)
st.set_page_config(page_title="বিরিয়ানি দিবে? | Biriyani Finder BD", page_icon="🍗", layout="wide")

CSV_FILE = 'mosque_data.csv'

# ২. ডেটা লোড করার ফাংশন
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # ফাইল না থাকলে নতুন কলামসহ তৈরি করবে
        return pd.DataFrame(columns=['name', 'lat', 'lon', 'menu', 'type', 'district'])

# ৩. ডেটা সেভ করার ফাংশন
def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# ডেটা ইনিশিয়ালাইজ
df = load_data()

# ৪. মেইন হেডার
st.markdown("<h1 style='text-align: center; color: #E63946;'>🍗 বিরিয়ানি দিবে?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>রমজানের সেরা 'বিরিয়ানি ট্র্যাকার' - খাবেন নিজেও, খাওয়াবেন অন্যকেও! 🌙</p>", unsafe_allow_html=True)
st.divider()


# ৫. সাইডবার - নতুন স্পট অ্যাড করার ফানি ফর্ম
st.sidebar.markdown("## ➕ নতুন বিরিয়ানি স্পট!")
st.sidebar.info("উম্মাহকে ইফতার খুঁজে পেতে সাহায্য করুন! আপনার নাম ইতিহাসের পাতায় স্বর্ণাক্ষরে লেখা থাকবে। 😉")

# সেশন স্টেটে লোকেশন স্টোর করা (ম্যাপ ক্লিক হ্যান্ডেল করার জন্য)
if 'lat' not in st.session_state: st.session_state.lat = 23.8103
if 'lon' not in st.session_state: st.session_state.lon = 90.4125

# ১. জিপিএস বাটন
if st.sidebar.button("🛰️ আমার বর্তমান লোকেশন নিন"):
    loc = get_geolocation()
    if loc:
        st.session_state.lat = loc['coords']['latitude']
        st.session_state.lon = loc['coords']['longitude']
        st.toast("বুম! আপনার জিপিএস লোকেশন লক করা হয়েছে। 🎯")
        st.rerun()

# ২. ফর্ম ইনপুট (ম্যাপের বাইরে থাকা ভ্যালুগুলো দেখাবে)
with st.sidebar.form("add_info_form", clear_on_submit=True):
    new_name = st.text_input("🕌 মসজিদের নাম", placeholder="যেমন: সোবহানবাগ জামে মসজিদ")
    new_dist = st.text_input("📍 জেলা/মহল্লা", placeholder="যেমন: ধানমন্ডি, ঢাকা")
    new_menu = st.selectbox("🍱 আজকের স্পেশাল মেনু কী?", 
                            ["কাচ্চি বিরিয়ানি 🍗", "শাহী তেহারি 🍚", "খিচুড়ি উৎসব 🥘", "তেলে ভাজা ইফতার 🍛", "অন্যান্য"])
    
    st.write(f"নির্বাচিত লোকেশন: `{st.session_state.lat:.4f}, {st.session_state.lon:.4f}`")
    st.caption("💡 মূল ম্যাপে যেকোনো জায়গায় ক্লিক করে লোকেশন পরিবর্তন করতে পারেন।")
    
    helper_name = st.text_input("👑 এই পুণ্য কাজের কারিগর কে?", placeholder="আপনার নাম")
    
    submit = st.form_submit_button("ব্যাস, এই স্পটটি ম্যাপে ঢুকিয়ে দিন! 🚀")
    
    if submit:
        if new_name and helper_name:
            new_type = "Biriyani" if any(x in new_menu for x in ["বিরিয়ানি", "তেহারি"]) else "Iftar"
            new_entry = {
                "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", "type": new_type, "district": new_dist
            }
            save_data(new_entry) 
            st.balloons() 
            st.success(f"অভিনন্দন {helper_name} ভাই! আপনি তো পুরাই 'বিরিয়ানি লিজেন্ড'! 🌟")
            st.rerun()
        else:
            st.warning("সবগুলো ঘর পূরণ করুন! কিপটেমি করলে কিন্তু বিরিয়ানি ঠান্ডা হয়ে যাবে! 🛑")

# ৬. মেইন ম্যাপ ডিসপ্লে (এটিই এখন ইনপুট হিসেবে কাজ করবে)
st.subheader("📍 বর্তমানের বিরিয়ানি পয়েন্টগুলো (ম্যাপে ক্লিক করে নতুন লোকেশন সিলেক্ট করুন)")

# ম্যাপ তৈরি
m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=12)

# ডাটাবেজে থাকা সব মার্কার যোগ করা
for index, row in df.iterrows():
    icon_color = "green" if row['type'] == "Biriyani" else "blue"
    folium.Marker(
        [row['lat'], row['lon']],
        popup=row['name'],
        icon=folium.Icon(color=icon_color, icon="cutlery", prefix='fa')
    ).add_to(m)

# ইউজারের বর্তমানে সিলেক্ট করা লাল পিন (📍 Indicator)
folium.Marker(
    [st.session_state.lat, st.session_state.lon],
    tooltip="নতুন স্পট এখানে?",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# ম্যাপ রেন্ডার করা
map_data = st_folium(m, width="100%", height=550, key="main_map")

# ম্যাপে যেকোনো জায়গায় ক্লিক করলে সেশন স্টেট আপডেট হবে
if map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lng = map_data["last_clicked"]["lng"]
    
    if clicked_lat != st.session_state.lat:
        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lng
        st.rerun()
        
        
# ৭. ডেটা টেবিল এবং ফুটনোট
st.write("---")
col_info, col_table = st.columns([1, 1])

with col_info:
    st.markdown("### 💡 কিছু কথা")
    st.write("- ম্যাপের পিনে ক্লিক করলে গুগল ম্যাপের লিঙ্ক পাবেন।")
    st.write("- কোনো তথ্য ভুল হলে বা বিরিয়ানি না দিলে আমাদের মাফ করে দিয়েন! 🙏")
    st.write("- বেশি বেশি শেয়ার করুন যাতে কেউ অভুক্ত না থাকে।")

with col_table:
    if st.checkbox("📋 সব লোকেশনের লিস্ট দেখুন"):
        st.dataframe(df[['name', 'district', 'menu']], use_container_width=True)

# ফুটারে আপনার নাম এবং ফেসবুক লিঙ্ক (বড় সাইজ এবং ইন্টারেক্টিভ)
st.write("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 18px;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)