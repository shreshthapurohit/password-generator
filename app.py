import streamlit as st
import random
import string
import pyperclip
import json
import os

DATA_FILE = "passwords.json"

# ---------- PASSWORD GENERATOR ----------
def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation

    if not chars:
        return None

    return "".join(random.choice(chars) for _ in range(length))


# ---------- STRENGTH ----------
def check_strength(password):
    score = 0
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1

    if len(password) >= 12 and score >= 3:
        return "🟢 Strong"
    elif len(password) >= 8:
        return "🟡 Medium"
    else:
        return "🔴 Weak"


# ---------- DATA ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    return json.load(open(DATA_FILE))


def save_data(data):
    json.dump(data, open(DATA_FILE, "w"), indent=2)


# ---------- UI ----------
st.set_page_config(page_title="Password Manager", page_icon="🔐")
st.title("🔐 Advanced Password Generator & Manager")

menu = st.sidebar.selectbox("Menu", ["Generate", "Save", "View"])

data = load_data()

# ---------- GENERATE ----------
if menu == "Generate":
    st.subheader("Generate Password")

    col1, col2 = st.columns(2)

    with col1:
        use_upper = st.checkbox("Uppercase", True)
        use_lower = st.checkbox("Lowercase", True)

    with col2:
        use_digits = st.checkbox("Numbers", True)
        use_symbols = st.checkbox("Symbols", True)

    length = st.slider("Length", 4, 30, 10)

    if st.button("Generate"):
        pwd = generate_password(length, use_upper, use_lower, use_digits, use_symbols)

        if not pwd:
            st.error("Select at least one option")
        else:
            st.session_state["pwd"] = pwd

# ---------- DISPLAY ----------
if "pwd" in st.session_state:
    pwd = st.session_state["pwd"]

    st.success("Password Generated!")

    show = st.checkbox("Show Password")
    if show:
        st.code(pwd)
    else:
        st.code("*" * len(pwd))

    st.write("Strength:", check_strength(pwd))

    # copy
    if st.button("📋 Copy Password"):
        pyperclip.copy(pwd)
        st.success("Copied!")

# ---------- SAVE ----------
if menu == "Save":
    st.subheader("Save Password")

    site = st.text_input("Website")
    username = st.text_input("Username")
    password = st.text_input("Password", value=st.session_state.get("pwd", ""), type="password")

    if st.button("Save"):
        if site and username and password:
            data[site] = {"username": username, "password": password}
            save_data(data)
            st.success("Saved successfully!")
        else:
            st.error("Fill all fields")

# ---------- VIEW ----------
if menu == "View":
    st.subheader("Saved Passwords")

    if data:
        for site, info in data.items():
            with st.expander(site):
                st.write("Username:", info["username"])
                st.write("Password:", info["password"])

        # download
        st.download_button(
            "📥 Download Data",
            data=json.dumps(data, indent=2),
            file_name="passwords.json"
        )
    else:
        st.info("No passwords saved")