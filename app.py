import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Grindery GPT", layout="centered")

st.title("🤖 Grindery GPT - Data Analyst Assistant")

prompt = st.text_area("Describe tu análisis de datos:", height=100)
submit = st.button("Ejecutar análisis")

if submit and prompt:
    with st.spinner("Consultando datos..."):
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
                st.success("✅ Consulta completada")

                # Mostrar resumen
                st.subheader("📝 Resumen del análisis")
                st.write(data["response"])

                # Mostrar tabla
                df = pd.DataFrame(data["result"])
                st.subheader("📊 Resultados")
                st.dataframe(df)

                # Exportar CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Descargar CSV", data=csv, file_name="resultado.csv", mime="text/csv")

                # Mostrar gráfico si hay columnas date + valor
                if "date" in df.columns and len(df.columns) >= 2:
                    value_column = [col for col in df.columns if col != "date"][0]
                    chart = alt.Chart(df).mark_line(point=True).encode(
                        x="date:T",
                        y=alt.Y(value_column, title=value_column.replace("_", " ").title())
                    ).properties(title="📈 Tendencia")
                    st.altair_chart(chart, use_container_width=True)

                # Mostrar SQL
                with st.expander("📄 SQL generada"):
                    st.code(data["sql"], language="sql")

                # Costo estimado
                if "estimated_cost_usd" in data:
                    st.caption(f"💰 Costo estimado: ${data['estimated_cost_usd']:.6f}")

        except Exception as e:
            st.error(f"❌ Error al procesar: {str(e)}")
