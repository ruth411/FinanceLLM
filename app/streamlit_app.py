import os, requests, pandas as pd
import streamlit as st
import plotly.express as px

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="FinanceLLM", layout="wide")
st.title("💸 FinanceLLM – Local LLM Dashboard")

with st.sidebar:
    st.header("Upload CSV")
    f = st.file_uploader("Bank/CC statement (CSV)", type=["csv"])
    acct = st.text_input("Account hint (optional)")
    if st.button("Ingest") and f is not None:
        r = requests.post(f"{API_BASE}/ingest",
                          files={"file": (f.name, f.read(), "text/csv")},
                          data={"account": acct})
        st.success(r.json())

    st.header("Budget Rules")
    pat = st.text_input("Pattern (substring)")
    cat = st.text_input("Category")
    if st.button("Add Rule") and pat and cat:
        r = requests.post(f"{API_BASE}/rules", json={"pattern": pat, "category": cat})
        st.success(r.json())

st.subheader("Overview")
try:
    ms = requests.get(f"{API_BASE}/summary/monthly").json()
    df_m = pd.DataFrame(ms)
    if not df_m.empty:
        fig = px.line(df_m, x="month", y="net", markers=True, title="Monthly Net (income + / expenses -)")
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info(f"API not ready yet: {e}")

st.subheader("Category Breakdown")
month = st.text_input("Month filter (YYYY-MM)")
try:
    catd = requests.get(f"{API_BASE}/summary/by_category",
                        params={"month": month or None}).json()
    df_c = pd.DataFrame(catd)
    if not df_c.empty:
        fig = px.bar(df_c, x="category", y="net", title="By Category")
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info(f"API not ready yet: {e}")

col1, col2 = st.columns([2,1])
with col1:
    st.subheader("Recent Transactions")
    try:
        tx = requests.get(f"{API_BASE}/transactions", params={"limit": 200}).json()
        st.dataframe(pd.DataFrame(tx))
    except Exception as e:
        st.info(f"API not ready yet: {e}")

with col2:
    st.subheader("Ask the LLM")
    q = st.text_area("Question", placeholder="e.g., What’s my grocery spend in Aug 2025?")
    if st.button("Ask") and q.strip():
        try:
            a = requests.post(f"{API_BASE}/ask", json={"question": q}).json()
            st.write(a.get("answer", ""))
        except Exception as e:
            st.error(f"LLM bridge error: {e}")