import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Grindery GPT", layout="centered")
st.title("🤖 Grindery GPT - Data Analyst Assistant")

# ✅ Leer el prompt desde los parámetros de la URL
query_params = st.query_params
prompt = query_params.get("prompt", "")
default_prompt = prompt or ""

# ✅ Cuadro de texto
prompt_input = st.text_area("Describe your data analysis:", value=default_prompt, height=100)
submit = st.button("Run analysis")

if submit and prompt_input:
    with st.spinner("Querying data..."):
        try:
            response = requests.post(
                "https://grindery-gpt-824949430451.europe-west1.run.app/ask",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt_input}
            )
            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Query completed")

                # Summary
                st.subheader("📝 Summary")
                st.write(data["response"])

                # Table
                df = pd.DataFrame(data["result"])
                st.subheader("📊 Results")
                st.dataframe(df)

                # Export CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", data=csv, file_name="result.csv", mime="text/csv")

                # Chart
                if "date" in df.columns and len(df.columns) >= 2:
                    value_column = [col for col in df.columns if col != "date"][0]
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x="date:T",
                        y=alt.Y(value_column, title=value_column.replace("_", " ").title())
                    ).properties(title="📈 Trend")
                    st.altair_chart(chart, use_container_width=True)

                # SQL
                with st.expander("📄 SQL generated"):
                    st.code(data["sql"], language="sql")

                # Cost
                if "estimated_cost_usd" in data:
                    st.caption(f"💰 Estimated cost: ${data['estimated_cost_usd']:.6f}")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
