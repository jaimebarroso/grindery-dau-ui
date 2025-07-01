import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="Grindery GPT", layout="centered")
st.title("📊 Grindery GPT")

with st.expander("ℹ️ Useful examples", expanded=True):
    st.markdown("""
    Try asking:
    - "Show DAU trend for the last 14 days grouped by date."
    - "Break down DAU by user type."
    """)

prompt = st.text_area("Your question", placeholder="Show DAU trend for the last 14 days grouped by date.")
ask_button = st.button("Ask")

if ask_button and prompt:
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                "https://grindery-gpt-824949430451.europe-west1.run.app/ask",
                json={"prompt": prompt},
                timeout=60
            )
            data = response.json()

            if "error" in data:
                st.error("❌ " + data["error"])
            else:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader("🧠 AI Summary")
                    st.write(data["response"])
                with col2:
                    if "estimated_cost_usd" in data:
                        st.metric(label="💰 Estimated Cost (USD)", value=f"${data['estimated_cost_usd']:.6f}")

                st.subheader("📈 Chart (if available)")
                df = pd.DataFrame(data["result"])

                # Try to auto-detect a date + numeric value column to chart
                if not df.empty:
                    date_cols = df.select_dtypes(include=["datetime64[ns]", "object"]).columns
                    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

                    chart_drawn = False
                    for date_col in date_cols:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                            if df[date_col].notna().all():
                                for num_col in numeric_cols:
                                    base = alt.Chart(df).encode(
                                        x=alt.X(f"{date_col}:T", title="Date"),
                                        y=alt.Y(f"{num_col}:Q", title=num_col.replace("_", " ").title())
                                    )
                                    line = base.mark_line(point=True).encode(
                                        tooltip=[f"{date_col}:T", f"{num_col}:Q"]
                                    )
                                    trend = base.transform_regression(
                                        date_col, num_col
                                    ).mark_line(
                                        strokeDash=[5, 5], color="gray"
                                    ).encode(
                                        tooltip=[f"{date_col}:T", f"{num_col}:Q"]
                                    )
                                    st.altair_chart(line + trend, use_container_width=True)
                                    chart_drawn = True
                                    break
                        except Exception:
                            continue
                        if chart_drawn:
                            break

                st.subheader("📋 Result Table")
                st.dataframe(df)

                st.subheader("🧾 SQL Used")
                st.code(data["sql"], language="sql")

        except requests.exceptions.Timeout:
            st.error("❌ It took too long. Try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 Error contacting backend: {str(e)}")
        except Exception as e:
            st.error(f"🚨 Unexpected Error: {str(e)}")
