import streamlit as st

from utils import handle_login, handle_chat, sign_up
from utils import get_session_messages, get_user_sessions
from utils import handle_create_session


# Main app
def main():
    st.title("This is JUST ANOTHER CHATBOT")

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "current_session" not in st.session_state:
        st.session_state.current_session = None
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "creating_new_session" not in st.session_state:
        st.session_state.creating_new_session = False
    if "needs_rerun" not in st.session_state:
        st.session_state.needs_rerun = False

    if st.session_state.needs_rerun:
        st.session_state.needs_rerun = False
        st.rerun()

    # Authentication section
    if not st.session_state.authenticated:
        auth_tab, register_tab = st.tabs(["Sign In", "Sign Up"])

        with auth_tab:
            st.subheader("Sign In")
            st.text_input("Username", key="login_username")
            st.text_input(
                "Password",
                type="password",
                key="login_password",
                on_change=handle_login,
            )

            st.button("Sign In", on_click=handle_login)

        with register_tab:
            st.subheader("Sign Up")
            reg_username = st.text_input("Username", key="reg_username")
            reg_password = st.text_input(
                "Password", type="password", key="reg_password"
            )
            reg_confirm = st.text_input(
                "Confirm Password", type="password", key="reg_confirm"
            )

            if st.button("Create Account"):
                if reg_password != reg_confirm:
                    st.error("Passwords don't match")
                else:
                    success, message = sign_up(reg_username, reg_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    else:  # If authenticated
        st.sidebar.title(f"Welcome, {st.session_state.username}!")

        # Session management in sidebar
        st.sidebar.subheader("Chat Sessions")

        # Button to create new session
        if st.sidebar.button("➕ New Session"):
            st.session_state.creating_new_session = True

        if st.session_state.creating_new_session:
            st.sidebar.text_input(
                "Session Name (optional)",
                key="session_name",
                placeholder="Enter name for this session",
            )
            col1, col2 = st.sidebar.columns(2)
            if col1.button("Create"):
                handle_create_session()
                if st.session_state.get("session_name"):
                    pass
                st.rerun()
            if col2.button("Cancel"):
                st.session_state.creating_new_session = False
                st.rerun()
        # List of previous sessions
        user_sessions = get_user_sessions(st.session_state.username)
        if user_sessions:
            st.sidebar.subheader("History")
            for session_id, session_data in user_sessions.items():
                display_text = session_data.get("name", session_data["created_at"])
                if st.sidebar.button(display_text):
                    st.session_state.current_session = session_id
                    st.rerun()

        # Sign out button
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Sign Out"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_session = None
            st.rerun()

        # Main chat interface
        if st.session_state.current_session:
            st.subheader("Chat")

            # Display chat messages
            messages = get_session_messages(
                st.session_state.username, st.session_state.current_session
            )

            for msg in messages:
                with st.chat_message(msg["sender"]):
                    st.write(msg["message"])
            # User input
            if user_message := st.chat_input("Type your message"):
                handle_chat(user_message)

            # st.button("Send", on_click=handle_chat)

        else:
            st.info("Select a chat session or create a new one.")


if __name__ == "__main__":
    main()
