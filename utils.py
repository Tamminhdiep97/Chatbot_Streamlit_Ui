import os
import json
import time
import uuid
from datetime import datetime

import streamlit as st
import numpy as np
from loguru import logger


# File paths
USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"

# Initialize files if they don't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(SESSIONS_FILE):
    with open(SESSIONS_FILE, "w") as f:
        json.dump({}, f)


# Load data
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def load_sessions():
    with open(SESSIONS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def save_sessions(sessions):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)


def handle_login():
    """Handle login when Enter is pressed in password field"""
    if st.session_state.login_password:
        success, message = sign_in(
            st.session_state.login_username, st.session_state.login_password
        )
        if success:
            st.session_state.authenticated = True
            st.session_state.username = st.session_state.login_username
            st.session_state.needs_rerun = True
        else:
            st.error(message)


def handle_create_session():
    session_name = st.session_state.get("session_name")
    logger.info("HANDLE: {}".format(st.session_state.session_name))
    session_id = create_new_session(st.session_state.username, session_name)
    st.session_state.current_session = session_id
    st.session_state.create_new_session = False
    st.session_state.needs_rerun = True


def handle_chat(user_input):
    """Handle chat message when Enter is pressed"""
    with st.chat_message("user"):
        st.markdown(user_input)
        # Add user message to session
    add_message_to_session(
        st.session_state.username, st.session_state.current_session, "user", user_input,
    )

    # Add bot response to session
    with st.chat_message("Chatbot"):
        with st.spinner("Please wait a bit..."):
            time.sleep(np.random.randint(10))
            bot_response = get_bot_response(user_input)
        st.markdown(bot_response)

    add_message_to_session(
        st.session_state.username,
        st.session_state.current_session,
        "Chatbot",
        bot_response,
    )
    pass

    # Clear input
    # st.session_state.needs_rerun = True


# Authentication functions
def sign_up(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    users[username] = {"password": password}
    save_users(users)
    return True, "Sign up successful"


def sign_in(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found"
    if users[username]["password"] != password:
        return False, "Incorrect password"
    return True, "Sign in successful"


# Session functions
def create_new_session(username, session_name=None):
    sessions = load_sessions()
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if username not in sessions:
        sessions[username] = {}

    logger.info("Session name: {}".format(session_name))
    sessions[username][session_id] = {
        "created_at": timestamp,
        "messages": [],
        "name": session_name or timestamp,
    }
    save_sessions(sessions)
    return session_id


def get_user_sessions(username):
    sessions = load_sessions()
    return sessions.get(username, {})


def get_session_messages(username, session_id):
    sessions = load_sessions()
    return sessions.get(username, {}).get(session_id, {}).get("messages", [])


def add_message_to_session(username, session_id, sender, message):
    sessions = load_sessions()
    sessions[username][session_id]["messages"].append(
        {
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    save_sessions(sessions)


# Chatbot response function (simple echo for demo)
def get_bot_response(user_input):
    return f"I received: {user_input}"
