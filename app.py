import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Grindery GPT", layout="centered")
st.title("🤖 Grindery GPT - Data Analyst Assistant (via n8n)")

# 🧠 Prompt
prompt = st.text_area("Describe your data analysis question:", height=100)
submit = st.button("Run Analysis")

if submit and prompt:
    with st.spinner("Processing your request..."):
        try:
            # ✅ Send prompt to n8n webhook (instead of Cloud Run directly)
            response = requests.post(
                "https://grindery.app.n8n.cloud/webhook-test/analytics-agent",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt}
            )
            data = response.json()

            # ✅ Check for error
            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Analysis completed")

                # 📝 Summary
                st.subheader("📝 Analysis Summary")
                st.write(data.get("response", "No summary available."))

                # 📊 Result Table
                df = pd.DataFrame(data.get("result", []))
                st.subheader("📊 Query Results")
                if df.empty:
                    st.warning("The query returned no data.")
                else:
                    st.dataframe(df)

                    # ⬇️ Export as CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", data=csv, file_name="result.csv", mime="text/csv")

                    # 📈 Chart (if date + value)
                    if "date" in df.columns and len(df.columns) >= 2:
                        value_col = [c for c in df.columns if c != "date"][0]
                        chart = alt.Chart(df).mark_line(point=True).encode(
                            x="date:T",
                            y=alt.Y(value_col, title=value_col.replace("_", " ").title())
                        ).properties(title="📈 Trend")
                        st.altair_chart(chart, use_container_width=True)

                # 🧾 SQL
                if "sql" in data:
                    with st.expander("📄 Generated SQL"):
                        st.code(data["sql"], language="sql")

                # 💰 Cost estimate
                if "estimated_cost_usd" in data:
                    st.caption(f"💰 Estimated Cost: ${data['estimated_cost_usd']:.6f}")

        except Exception as e:
            st.error(f"❌ Error processing request: {str(e)}")
