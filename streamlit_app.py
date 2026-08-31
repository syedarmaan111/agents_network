import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")
CHATBOT_OPTIONS = {
    "🛠️ Engineer": "engineer",
    "🩺 Doctor": "doctor",
    "⚖️ Lawyer": "lawyer",
}


def reset_chat() -> None:
    st.session_state.conversation_id = None
    st.session_state.messages = []


def login_screen() -> None:
    st.title("Agent Chat")
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")

        if submitted:
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                    timeout=15,
                )
                data = response.json()
            except requests.RequestException:
                st.error("Unable to reach the FastAPI server.")
                return
            except ValueError:
                st.error("The FastAPI server returned an invalid response.")
                return

            if response.ok:
                st.session_state.token = data["access_token"]
                reset_chat()
                st.rerun()

            st.error(data.get("message", "Login failed"))

    with register_tab:
        with st.form("register_form"):
            register_email = st.text_input("Email", key="register_email")
            register_password = st.text_input(
                "Password",
                type="password",
                key="register_password",
            )
            register_submitted = st.form_submit_button("Register")

        if register_submitted:
            try:
                response = requests.post(
                    f"{API_URL}/auth/register",
                    json={"email": register_email, "password": register_password},
                    timeout=15,
                )
                data = response.json()
            except requests.RequestException:
                st.error("Unable to reach the FastAPI server.")
                return
            except ValueError:
                st.error("The FastAPI server returned an invalid response.")
                return

            if response.ok:
                st.success("Registration successful. Please log in.")
            else:
                st.error(data.get("message", "Registration failed"))


def chat_screen() -> None:
    st.title("Agent Chat")

    selected_label = st.selectbox(
        "Select chatbot:",
        options=list(CHATBOT_OPTIONS),
        key="chatbot_label",
    )
    chatbot_type = CHATBOT_OPTIONS[selected_label]
    if st.session_state.selected_chatbot_type != chatbot_type:
        st.session_state.selected_chatbot_type = chatbot_type
        reset_chat()
        st.rerun()

    if st.button("Logout"):
        try:
            requests.post(
                f"{API_URL}/auth/logout",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                timeout=15,
            )
        except requests.RequestException:
            pass
        st.session_state.clear()
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Send a message")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        try:
            response = requests.post(
                f"{API_URL}/chat",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                json={
                    "message": prompt,
                    "conversation_id": st.session_state.conversation_id,
                    "chatbot_type": chatbot_type,
                },
                timeout=60,
            )
            data = response.json()
        except requests.RequestException:
            st.error("Unable to reach the FastAPI server.")
            return
        except ValueError:
            st.error("The FastAPI server returned an invalid response.")
            return

        if not response.ok or data.get("error"):
            st.error(data.get("message", "Chat request failed"))
            st.session_state.messages.pop()
            return

        st.session_state.conversation_id = data["conversation_id"]
        st.session_state.messages.append(
            {"role": "assistant", "content": data["response"]}
        )
        with st.chat_message("assistant"):
            st.write(data["response"])


def main() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("selected_chatbot_type", "engineer")
    st.session_state.setdefault("chatbot_label", "🛠️ Engineer")

    if st.session_state.token:
        chat_screen()
    else:
        login_screen()


if __name__ == "__main__":
    main()
