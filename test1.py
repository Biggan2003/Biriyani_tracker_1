import streamlit as st
from streamlit_gsheets import GSheetsConnection
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
#st.markdown("<h3 style='text-align: center; color: #E63946; margin-bottom: 0; font-size: 20px;'>🌙 রমজানের সেরা  বিরিয়ানি 🍗 ট্র্যাকার</h2>", unsafe_allow_html=True)
# (বিরিয়ানি শব্দে সোনালী রঙ সহ)
st.markdown("""
    <h3 style='text-align: center; margin-bottom: 0; font-size: 20px; font-family: "SolaimanLipi", sans-serif;'>
        <span style='color: #E63946;'>🍗 রমজানের সেরা  </span>
        <span style='color: #FFD700; text-shadow: 1px 1px #000;'>বিরিয়ানি</span>
        <span style='color: #E63946;'> ট্র্যাকার</span>
    </h3>
""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: ; color: white; font-size: 14px; text-shadow: 1px 1px 2px black;'>আপনার মহল্লার বিরিয়ানি 🥘 এখন আপনার হাতের মুঠোয় </p>", unsafe_allow_html=True)
#st.markdown("<p style='text-align: center; font-style: italic; color: #2D6A4F; font-size: 13px; margin-top: 0;'>আপনার মহল্লার বিরিয়ানি 🥘 এখন আপনার হাতের মুঠোয়!</p>", unsafe_allow_html=True)
#st.markdown("<p style='text-align: center; font-style: italic; color: #555;'>আপনার মহল্লার বিরিয়ানি 🥘 এখন আপনার হাতের মুঠোয়! </p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 বিরিয়ানি খুঁজুন", "➕ বিরিয়ানি স্পট যোগ করুন"])

# --- TAB 1: বিরিয়ানি খোঁজা ---
with tab1:
    st.subheader("📍 বিরিয়ানি ম্যাপ")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=st.session_state.zoom)

    for index, row in df.iterrows():
        # বিরিয়ানি হলে লেগ পিস, না হলে অন্য খাবারের ইমোজি
        food_emoji = "🍗" if row['type'] == "Biriyani" else "🍲"
        
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
        
        # ডিফল্ট আইকনের বদলে ইমোজি আইকন ব্যবহার
        folium.Marker(
            [row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=180),
            tooltip=row['name'],
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 24px; background: white; border-radius: 50%; 
                         width: 35px; height: 35px; display: flex; justify-content: center; 
                         align-items: center; border: 2px solid #E63946; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
                         {food_emoji}
                         </div>""",
                icon_anchor=(17, 17) # আইকনটি ঠিক লোকেশনের ওপর বসানোর জন্য
            )
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
    
        # মেসেজ দেখানোর জন্য একটি খালি জায়গা (placeholder) তৈরি করে রাখা
        message_place = st.empty()
    
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✅ আলহামদুলিল্লাহ, পেয়েছি  : {df.at[idx, 'real']}", use_container_width=True):
                df.at[idx, 'real'] += 1
                df.to_csv(CSV_FILE, index=False)
                # বাটনের ঠিক উপরে মেসেজটি দেখাবে
                message_place.success("ইতিহাস আপনাকে মনে রাখবে! 😉")
                import time
                time.sleep(4) # ২ সেকেন্ড মেসেজটি দেখিয়ে তারপর পেজ রিলোড হবে
                st.rerun()
            
        with col2:
            if st.button(f"❌ ভুয়া: {df.at[idx, 'fake']}", use_container_width=True):
                df.at[idx, 'fake'] += 1
                df.to_csv(CSV_FILE, index=False)
                # বাটনের ঠিক উপরে মেসেজটি দেখাবে
                message_place.error("মানুষকে বাঁচানোর জন্য ধন্যবাদ! 🛑")
                import time
                time.sleep(3)
                st.rerun()
    else:
        #st.info("💡 কোনো একটি মসজিদের পিনে (Marker) ক্লিক করুন ভোট দেওয়ার জন্য!")
        st.info("💡 ম্যাপের মসজিদের (পিনে) ক্লিক করে জাতিকে বিরিয়ানির সন্ধান দিন! আপনার একটা সঠিক তথ্য হাজারো বিরিয়ানি Lover-এর মুখে হাসি (আর পেটে শান্তি) ফোটাতে পারে। 🍗🚀")



# --- TAB 2: ফানি মোড ও ফ্লোটিং টার্গেট (Fixed CSS) ---
with tab2:
    # বাটন সেন্টারে নেওয়ার জন্য শক্তিশালী CSS
    st.markdown("""
        <style>
        /* ফর্মের সাবমিট বাটনকে টার্গেট করা */
        .stFormSubmitButton {
            display: flex;
            justify-content: center;
        }
    
        .stFormSubmitButton > button {
            width: 100% !important;
            max-width: 300px !important;
            background-color: #E63946 !important; /* বিরিয়ানি লাল রঙ */
            color: white !important;
            border-radius: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    
    #st.markdown("### ➕ নতুন স্পট যোগ করুন")
    st.write(" ম্যাপের মাঝখানের **'🎯 Mosjid'** চিহ্নের নিচে সঠিক জায়গাটি আনুন এবং সেখানে ক্লিক করুন।")
    
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
            
        new_name = st.text_input("🕌 মসজিদের নাম", placeholder="যেমন: লালবাগ শাহী মসজিদ")
        new_dist = st.text_input("📍 জেলা", placeholder="যেমন: ঢাকা")
        
        # আপনার হারানো স্পেশাল মেনু সেকশন
        new_menu = st.selectbox("🥘 আইটেম সিলেক্ট করুন (যেমন: বিরিয়ানি/ ছোলা-মুড়ি)", [
            "বিরিয়ানি 🍗", 
            "শাহী তেহারি 🍚", 
            "খিচুড়ি ও মাংস 🥘", 
            "ছোলা-মুড়ি আর জিলাপি 🥨",
            "বুট-মুড়ি ও ভাজাপোড়া 🍲",
            "স্পেশাল ইফতার বক্স 🍱",
            
        ])
        
        helper_name = st.text_input("👑 বিরিয়ানির মহান দাতা, আপনার নামটা লিখুন", placeholder="যেমন: বিরিয়ানি খোর কাবিরুল ")
        
        # আরও কিছু ফানি টেক্সট যোগ করা হলো
        st.write("---")
        funny_quotes = [
            #"🍗 আপনিই কি সেই আসল বিরিয়ানি খোর? \nআপনার একটি সঠিক তথ্য হাজারো ক্ষুধার্ত আত্মার মুখে হাসি ফোটাতে পারে!",
    
            #"🌙 বিরিয়ানি বীরের তথ্য দিয়ে জাতিকে চরম ধোকা থেকে উদ্ধার করুন! \nবিরিয়ানি না পাইলেও এই মহৎ কাজের সওয়াব কিন্তু মিস নাই! 😉",
    
            "🍗 আপনার দেওয়া এই একটি তথ্য হাজারো বিরিয়ানি Lover-এর মুখে হাসি আর পেটে শান্তি এনে দেবে! \nইতিহাস আপনাকে একজন 'বিরিয়ানি বীর' হিসেবে স্বর্ণাক্ষরে মনে রাখবে। 👑",
    
            "🥔 আলু ছোট হোক বা বড়, বিরিয়ানি হওয়াই আসল কথা! \nসঠিক তথ্য দিয়ে 🍗 বিরিয়ানি যোদ্ধাদের সাহায্য করুন, বিরিয়ানি প্রেমীরা আপনাকে আজীবন দোয়া করবে। ❤️",
    
            "🕵️‍♂️ গোয়েন্দা গিরি বাদ দিয়ে বিরিয়ানির সঠিক তথ্য দিন! \nআপনার এই মহান ত্যাগের কথা আগামী প্রজন্মকে গল্প করে শোনানো হবে। 🔥"
        ]
        import random
        st.info(random.choice(funny_quotes))
        
        
        # বাটনের ঠিক নিচেই মেসেজ দেখানোর জন্য একটি খালি জায়গা রাখা
        submit_message_place = st.empty()
        if st.form_submit_button("ম্যাপে যোগ করুন! 🚀 (জনকল্যাণে)"):
            if new_name and helper_name and st.session_state.get('has_clicked'):
                # ডাটা সেভ লজিক
                # যেহেতু আপনার সিলেক্ট বক্সে "বিরিয়ানি 🍗" বা "তেহারি 🍚" আছে, তাই এই নামগুলো দিয়ে চেক করছি
                if "বিরিয়ানি" in new_menu or "তেহারি" in new_menu:
                    food_type = "Biriyani"
                else:
                    food_type = "Iftar"
                    
                new_entry = {
                    "name": new_name, "lat": st.session_state.lat, "lon": st.session_state.lon, 
                    "menu": f"{new_menu} (তথ্যদাতা: {helper_name})", 
                    "type": food_type, "district": new_dist,
                    "real": 0, "fake": 0
                }
                pd.concat([load_data(), pd.DataFrame([new_entry])], ignore_index=True).to_csv(CSV_FILE, index=False)
                st.balloons()
                # এখন মেসেজটি বাটনের পাশেই (নিচে) দেখা যাবে
                submit_message_place.success(f"মাশাআল্লাহ বিরিয়ানি বীর {helper_name}! ইতিহাস আপনাকে স্বর্ণাক্ষরে মনে রাখবে। 👑")
                # একটু সময় দিন যাতে ইউজার মেসেজটা দেখতে পারে
                import time
                time.sleep(4)
                
                #st.success(f"মাশাআল্লাহ বিরিয়ানি বীর {helper_name}! আপনার সওয়াব কনফার্ম! 😉")
                st.rerun()
            else:
                submit_message_place.error("🛑 উঁহু! এভাবে অর্ধেক তথ্য দিলে বিরিয়ানি Lover রা আপনার ওপর রাগ করবে । সব পূরণ করুন আর ম্যাপে আসল স্পটটা সিলেক্ট করুন 🎯 ")

st.write("---")
st.markdown(f"<p style='text-align: center; font-size: 16px; color: gray;'>Made by <a href='https://www.facebook.com/md.biggan.1' target='_blank' style='color: #E63946; text-decoration: none;'>G. M Biggan</a></p>", unsafe_allow_html=True)
