import streamlit as st
import requests

st.set_page_config(page_title="Grindery GPT - Data Analyst", layout="centered")

st.title("🤖 Grindery GPT - Data Analyst Assistant")

# Detect prompt from URL (automático si viene vía ?prompt=)
prompt = st.experimental_get_query_params().get("prompt", [""])[0]

# Campo editable por si el usuario quiere cambiar el texto
user_prompt = st.text_area("Describe your data analysis:", value=prompt, key="prompt_input")

# Botón manual (sigue disponible)
run_button = st.button("Run analysis")

# Se ejecuta si se hace clic o si llegó desde URL con prompt
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
                
                # Mostrar resumen
                if "summary" in result:
                    st.write("### Summary")
                    st.markdown(result["summary"])

                # Mostrar resultados en tabla
                if "result" in result:
                    st.write("### Result")
                    st.dataframe(result["result"])

                # Mostrar gráfico si está disponible
                if "chart" in result:
                    st.write("### Chart")
                    st.plotly_chart(result["chart"])

                # Mostrar SQL
                if "sql" in result:
                    st.write("### SQL")
                    st.code(result["sql"], language="sql")

                # Mostrar coste estimado si está disponible
                if "estimated_cost" in result:
                    st.caption(f"Estimated cost: ${result['estimated_cost']:.5f}")

            else:
                st.error("Failed to generate analysis.")
                st.text(response.text)

        except Exception as e:
            st.error("Something went wrong.")
            st.exception(e)
