import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Grindery GPT", layout="centered")

st.title("🤖 Grindery GPT - Data Analyst Assistant")

# ✅ Get prompt from query parameter (automático al abrir)
query_params = st.query_params
prompt = query_params.get("prompt", [""])[0].strip()

if not prompt:
    st.info("Add a prompt in the URL query like `?prompt=Show DAU trend for last 14 days`")
    st.stop()

st.markdown(f"**Prompt:** `{prompt}`")
st.markdown("---")

# 🔄 Call the backend endpoint
with st.spinner("Generating response..."):
    try:
        response = requests.post(
            "https://grindery-gpt-824949430451.europe-west1.run.app/ask",
            json={"prompt": prompt},
            timeout=90
        )
        data = response.json()
    except Exception as e:
        st.error(f"❌ Failed to generate analysis.\n\n{e}")
        st.stop()

# ✅ Display summary
st.subheader("📄 Summary")
st.write(data.get("response", "No summary found."))

# ✅ Display SQL (toggle)
with st.expander("🧠 SQL generated"):
    st.code(data.get("sql", "No SQL found."), language="sql")

# ✅ Display estimated cost
cost = data.get("estimated_cost_usd")
if cost:
    st.info(f"Estimated cost: **${round(cost, 4)}**")

# ✅ Display result (table)
if "result" in data and isinstance(data["result"], list) and len(data["result"]) > 0:
    st.subheader("📊 Result Table")
    df = pd.DataFrame(data["result"])
    st.dataframe(df)

    # 📈 Optional chart (if date/time column exists)
    date_columns = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if date_columns and numeric_columns:
        date_col = date_columns[0]
        y_col = numeric_columns[0]

        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(by=date_col)

        st.subheader("📈 Trend")
        fig, ax = plt.subplots()
        ax.plot(df[date_col], df[y_col], marker="o")
        ax.set_xlabel(date_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} over time")
        st.pyplot(fig)

    # 📥 Download CSV
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download CSV", data=csv, file_name="analysis_result.csv", mime="text/csv")

else:
    st.warning("No result table returned.")
