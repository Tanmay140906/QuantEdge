# ── auth.py — QuantEdge login / signup UI ────────────────────────────────────
import streamlit as st
from database import create_user, login_user, init_db

init_db()

AUTH_CSS = """
<style>
.auth-wrap {
    max-width: 420px; margin: 60px auto 0;
}
.auth-logo {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem; font-weight: 700;
    background: linear-gradient(90deg, #00d4aa, #0094ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; text-align: center; margin-bottom: 4px;
}
.auth-tagline {
    text-align: center; font-size: 0.85rem; color: #4b5563;
    margin-bottom: 32px; font-weight: 300;
}
.auth-card {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 16px;
    padding: 32px 36px;
}
.auth-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem; font-weight: 700;
    color: #e8eaf0; margin-bottom: 24px;
    text-transform: uppercase; letter-spacing: 1px;
}
.auth-divider {
    border: none; border-top: 1px solid #1e2130;
    margin: 20px 0;
}
.auth-switch {
    text-align: center; font-size: 0.82rem;
    color: #4b5563; margin-top: 16px;
}
</style>
"""


def render_auth_page():
    """Renders login/signup. Returns True if user is now authenticated."""
    # Already logged in
    if st.session_state.get("user"):
        return True

    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Tabs for login / signup
    st.markdown("<div class='auth-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='auth-logo'>QuantEdge</div>", unsafe_allow_html=True)
    st.markdown("<div class='auth-tagline'>Multi-indicator algorithmic trading strategy</div>",
                unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Sign Up"])

    with tab_login:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            st.markdown("**Username**")
            username = st.text_input("username_l", placeholder="your_username",
                                     label_visibility="collapsed")
            st.markdown("**Password**")
            password = st.text_input("password_l", type="password",
                                     placeholder="••••••••",
                                     label_visibility="collapsed")
            submitted = st.form_submit_button("Login →", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                result = login_user(username, password)
                if result["ok"]:
                    st.session_state["user"] = result["user"]
                    st.session_state["page"] = "analysis"
                    st.rerun()
                else:
                    st.error(result["error"])

    with tab_signup:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.form("signup_form", clear_on_submit=True):
            st.markdown("**Username**")
            new_username = st.text_input("username_s", placeholder="choose_a_username",
                                         label_visibility="collapsed")
            st.markdown("**Email**")
            new_email = st.text_input("email_s", placeholder="you@example.com",
                                      label_visibility="collapsed")
            st.markdown("**Password**")
            new_password = st.text_input("password_s", type="password",
                                         placeholder="min 6 characters",
                                         label_visibility="collapsed")
            st.markdown("**Confirm Password**")
            confirm_pw = st.text_input("confirm_s", type="password",
                                       placeholder="repeat password",
                                       label_visibility="collapsed")
            submitted_s = st.form_submit_button("Create Account →", use_container_width=True)

        if submitted_s:
            if not all([new_username, new_email, new_password, confirm_pw]):
                st.error("Please fill in all fields.")
            elif len(new_username.strip()) < 3:
                st.error("Username must be at least 3 characters.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != confirm_pw:
                st.error("Passwords do not match.")
            elif "@" not in new_email or "." not in new_email:
                st.error("Please enter a valid email address.")
            else:
                result = create_user(new_username, new_email, new_password)
                if result["ok"]:
                    st.success("Account created! Please log in.")
                else:
                    st.error(result["error"])

    st.markdown("</div>", unsafe_allow_html=True)
    return False  # Not yet authenticated