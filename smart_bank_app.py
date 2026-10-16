import json
import os
import uuid
import hashlib
from datetime import datetime

import streamlit as st

# ------------------------------------------------------------
# Smart Bank AI - learning/demo project only, not real banking
# ------------------------------------------------------------
st.set_page_config(
    page_title="Smart Bank AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "smart_bank_data.json"


def hash_password(password: str) -> str:
    """Demo-only password hash. Use a proper auth provider in production."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("users"), dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {"users": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def new_account_number():
    return str(uuid.uuid4().int)[:10]


def create_user(data, username, password, full_name):
    username = username.strip().lower()
    if not username or not password or not full_name.strip():
        return False, "Please fill in every field."
    if len(password) < 6:
        return False, "For this demo, use a password with at least 6 characters."
    if username in data["users"]:
        return False, "That username already exists. Please choose another."
    data["users"][username] = {
        "full_name": full_name.strip(),
        "password_hash": hash_password(password),
        "account_number": new_account_number(),
        "balance": 10000.0,
        "transactions": [{
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Account opened",
            "amount": 10000.0,
            "note": "Demo opening balance",
        }],
    }
    save_data(data)
    return True, "Demo account created. You can now log in."


def format_pkr(amount):
    return f"PKR {amount:,.2f}"


def add_transaction(user, kind, amount, note=""):
    user["transactions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": float(amount),
        "note": note,
    })


def answer_bank_question(question, user=None):
    q = question.lower().strip()
    if any(word in q for word in ["balance", "how much", "amount", "money"]):
        if user is not None:
            return f"Your current demo balance is {format_pkr(user['balance'])}."
        return "Please log in to view your demo account balance."
    if any(word in q for word in ["deposit", "add money", "put money"]):
        return "To deposit, open the Deposit Money section, enter an amount greater than zero, and press Deposit."
    if any(word in q for word in ["withdraw", "take money", "cash out"]):
        return "To withdraw, open Withdraw Money, enter an amount within your available demo balance, and press Withdraw."
    if any(word in q for word in ["transaction", "history", "record"]):
        return "Your recent demo transactions appear in the Transaction History section."
    if any(word in q for word in ["account number", "account no"]):
        if user is not None:
            return f"Your demo account number is {user['account_number']}."
        return "Please log in to view your demo account number."
    if any(word in q for word in ["hello", "hi", "salam", "assalam"]):
        return "Hello! I am Smart Bank Assistant. You can ask me about your demo balance, deposits, withdrawals, or transaction history."
    if any(word in q for word in ["help", "what can you do", "support"]):
        return "I can explain how to use this demo: check balance, deposit, withdraw, account number, and transaction history."
    return "I can help with demo banking questions about balance, deposits, withdrawals, account number, and transaction history. This is a rule-based demo assistant, not a live AI or real bank service."


def show_auth(data):
    st.markdown("## Welcome to Smart Bank AI")
    st.caption("Create a demo account or log in to continue.")
    login_tab, register_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login = st.form_submit_button("Log in", use_container_width=True)
        if login:
            key = username.strip().lower()
            user = data["users"].get(key)
            if user and user["password_hash"] == hash_password(password):
                st.session_state["username"] = key
                st.rerun()
            else:
                st.error("Username or password is incorrect.")

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Full name", key="register_name")
            new_username = st.text_input("Choose a username", key="register_username")
            new_password = st.text_input("Choose a password (minimum 6 characters)", type="password", key="register_password")
            create = st.form_submit_button("Create demo account", use_container_width=True)
        if create:
            ok, message = create_user(data, new_username, new_password, full_name)
            if ok:
                st.success(message)
            else:
                st.error(message)


def main():
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(135deg, #f5f8ff 0%, #eef7f5 100%); }
        [data-testid="stSidebar"] { background: #102a43; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        .hero { padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#102a43,#147d78); color: white; margin-bottom: 1rem; }
        .hero h1 { color: white; margin: 0; }
        .hero p { color: #e7f6f5; margin-bottom: 0; }
        div[data-testid="stMetric"] { background: white; padding: 1rem; border: 1px solid #e0e7ef; border-radius: 14px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("🏦 Smart Bank AI")
    st.sidebar.caption("Personal banking demo")
    data = load_data()

    username = st.session_state.get("username")
    if not username or username not in data["users"]:
        show_auth(data)
        st.sidebar.info("Demo only — do not use real passwords or financial information.")
        return

    user = data["users"][username]
    st.sidebar.write(f"**Customer:** {user['full_name']}")
    st.sidebar.write(f"**Account:** {user['account_number']}")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Deposit Money", "Withdraw Money", "Transaction History", "Bank Assistant", "Account Details"],
    )
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.pop("username", None)
        st.rerun()

    st.markdown(
        f'<div class="hero"><h1>Smart Bank AI</h1><p>Welcome back, {user["full_name"]}! Manage your demo account in one place.</p></div>',
        unsafe_allow_html=True,
    )

    if page == "Dashboard":
        st.subheader("Account Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Available Balance", format_pkr(user["balance"]))
        c2.metric("Account Number", user["account_number"])
        c3.metric("Transactions", len(user["transactions"]))
        st.markdown("### Quick actions")
        q1, q2 = st.columns(2)
        with q1:
            st.info("**Deposit Money**\n\nUse the sidebar to add funds to your demo balance.")
        with q2:
            st.info("**Withdraw Money**\n\nWithdrawals cannot exceed your available demo balance.")
        st.caption("The opening balance is fictional and only for demonstration.")

    elif page == "Deposit Money":
        st.subheader("➕ Deposit Money")
        st.write(f"Current balance: **{format_pkr(user['balance'])}**")
        with st.form("deposit_form"):
            amount = st.number_input("Deposit amount (PKR)", min_value=0.0, step=100.0, value=0.0)
            note = st.text_input("Note (optional)", placeholder="e.g. Demo deposit")
            submitted = st.form_submit_button("Deposit", use_container_width=True)
        if submitted:
            if amount <= 0:
                st.error("Enter an amount greater than zero.")
            else:
                user["balance"] += amount
                add_transaction(user, "Deposit", amount, note.strip())
                save_data(data)
                st.success(f"Successfully deposited {format_pkr(amount)}.")
                st.rerun()

    elif page == "Withdraw Money":
        st.subheader("➖ Withdraw Money")
        st.write(f"Current balance: **{format_pkr(user['balance'])}**")
        with st.form("withdraw_form"):
            amount = st.number_input("Withdrawal amount (PKR)", min_value=0.0, step=100.0, value=0.0)
            note = st.text_input("Note (optional)", placeholder="e.g. Demo withdrawal")
            submitted = st.form_submit_button("Withdraw", use_container_width=True)
        if submitted:
            if amount <= 0:
                st.error("Enter an amount greater than zero.")
            elif amount > user["balance"]:
                st.error("Insufficient demo balance.")
            else:
                user["balance"] -= amount
                add_transaction(user, "Withdrawal", amount, note.strip())
                save_data(data)
                st.success(f"Successfully withdrew {format_pkr(amount)}.")
                st.rerun()

    elif page == "Transaction History":
        st.subheader("📋 Transaction History")
        if user["transactions"]:
            rows = list(reversed(user["transactions"]))
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.download_button(
                "Download transaction history (JSON)",
                data=json.dumps(rows, indent=2, ensure_ascii=False),
                file_name="smart_bank_transactions.json",
                mime="application/json",
            )
        else:
            st.info("No transactions yet.")

    elif page == "Bank Assistant":
        st.subheader("🤖 Smart Bank Assistant")
        st.caption("A simple rule-based assistant for this demo. It does not connect to a live AI service.")
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": "Hello! Ask me about your balance, deposits, withdrawals, account number, or transaction history."}
            ]
        for message in st.session_state["chat_messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        prompt = st.chat_input("Ask a banking question...")
        if prompt:
            st.session_state["chat_messages"].append({"role": "user", "content": prompt})
            reply = answer_bank_question(prompt, user)
            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
            st.rerun()

    elif page == "Account Details":
        st.subheader("👤 Account Details")
        st.write(f"**Full name:** {user['full_name']}")
        st.write(f"**Username:** {username}")
        st.write(f"**Demo account number:** {user['account_number']}")
        st.write(f"**Current balance:** {format_pkr(user['balance'])}")
        st.warning("This is a learning project. Password handling and account security are not suitable for production banking.")


if __name__ == "__main__":
    main()
