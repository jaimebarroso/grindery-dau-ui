import streamlit as st
import requests

st.set_page_config(page_title="Grindery GPT - Data Analyst", layout="centered")

st.title("🤖 Grindery GPT - Data Analyst Assistant")

# Obtener el parámetro 'prompt' desde la URL (nuevo método)
query_params = st.query_params
prompt = query_params.get("prompt", "")

# Campo editable visible para el usuario
user_prompt = st.text_area("Describe your data analysis:", value=prompt, key="prompt_input")

# Botón por si el usuario quiere lanzarlo manualmente
run_button = st.button("Run analysis")

# Ejecutar si el botón se presiona o si hay un prompt en la URL
if run_button or prompt:
    with st.spinner("Running analysis..."):
        try:
            response = requests.post(
                "https://grindery-gpt-824949430451.ew.r.appspot.com/ask",
                json={"prompt": user_prompt}
            )

            if response.ok:
                result = response.json()
                st.success("Analysis completed.")

                if "summary" in result:
                    st.write("### Summary")
                    st.markdown(result["summary"])

                if "result" in result:
                    st.write("### Result")
                    st.dataframe(result["result"])

                if "chart" in result:
                    st.write("### Chart")
                    st.plotly_chart(result["chart"])

                if "sql" in result:
                    st.write("### SQL")
                    st.code(result["sql"], language="sql")

                if "estimated_cost" in result:
                    st.caption(f"Estimated cost: ${result['estimated_cost']:.5f}")

            else:
                st.error("Failed to generate analysis.")
                st.text(response.text)

        except Exception as e:
            st.error("Something went wrong.")
            st.exception(e)
