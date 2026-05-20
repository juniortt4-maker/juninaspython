import streamlit as st
🚨 EVENTO COM MAIOR PÚBLICO PREVISTO:
{str(maior_publico[coluna_evento]).upper()} ({int(maior_publico[coluna_publico]):,} PESSOAS)

⚠️ EVENTO COM MENOR PÚBLICO PREVISTO:
{str(menor_publico[coluna_evento]).upper()} ({int(menor_publico[coluna_publico]):,} PESSOAS)

📊 MÉDIA GERAL DE PÚBLICO:
{media_geral:,.0f} PESSOAS

📈 MEDIANA DE PÚBLICO:
{mediana:,.0f} PESSOAS
""")

    st.subheader("🏆 RANKING OPERACIONAL DOS COMANDOS")

    ranking = (
        df_filtrado.groupby(coluna_comando)[coluna_publico]
        .agg(["sum", "mean", "count"])
        .reset_index()
    )

    ranking.columns = [
        "COMANDO",
        "PÚBLICO TOTAL",
        "MÉDIA PÚBLICO",
        "REGISTROS"
    ]

    st.dataframe(ranking, use_container_width=True)

    st.subheader("📄 DADOS OPERACIONAIS")

    pesquisa = st.text_input("🔎 PESQUISAR")

    tabela = df_filtrado.copy()

    if pesquisa:
        tabela = tabela[
            tabela.astype(str)
            .apply(lambda x: x.str.contains(pesquisa, case=False, na=False))
            .any(axis=1)
        ]

    st.dataframe(tabela, use_container_width=True, height=500)

    csv = tabela.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao.csv",
        mime="text/csv"
    )

    st.success(f"✅ DASHBOARD ATUALIZADO EM {horario}")

except Exception as erro:
    st.error(f"ERRO AO CARREGAR DADOS: {erro}")
