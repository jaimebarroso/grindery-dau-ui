import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Grindery GPT", layout="centered")

st.title("🤖 Grindery GPT - Data Analyst Assistant")

prompt = st.text_area("Describe your data analysis:", height=100)
submit = st.button("Run analysis")

if submit and prompt:
    with st.spinner("Querying data..."):
        try:
            response = requests.post(
                "https://grindery-gpt-824949430451.europe-west1.run.app/ask",
                headers={"Content-Type": "application/json"},
                json={"prompt": prompt}
            )
            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                st.success("✅ Query completed")

                # Show summary
                st.subheader("📝 Summary of the analysis")
                st.write(data["response"])

                # Show results table
                df = pd.DataFrame(data["result"])
                st.subheader("📊 Results")
                st.dataframe(df)

                # Download CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", data=csv, file_name="result.csv", mime="text/csv")

                # Show chart if there's a date column
                date_column = next((col for col in df.columns if "date" in col.lower()), None)
                if date_column and len(df.columns) >= 2:
                    value_column = [col for col in df.columns if col != date_column][0]
                    df[date_column] = pd.to_datetime(df[date_column])
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x=alt.X(date_column + ":T", title="Date"),
                        y=alt.Y(value_column, title=value_column.replace("_", " ").title())
                    ).properties(title="📈 Trend")
                    st.altair_chart(chart, use_container_width=True)

                # Show SQL
                with st.expander("📄 Generated SQL"):
                    st.code(data["sql"], language="sql")

                # Estimated cost
                if "estimated_cost_usd" in data:
                    st.caption(f"💰 Estimated cost: ${data['estimated_cost_usd']:.6f}")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
