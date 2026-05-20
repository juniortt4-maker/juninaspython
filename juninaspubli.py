import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata
import re

st.set_page_config(
    page_title="OPERAÇÃO - SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 OPERAÇÃO - SÃO JOÃO 2026")

st.markdown("""
<style>
.stApp {
    background: #0B0F14;
}

h1, h2, h3 {
    color: #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

url = "https://docs.google.com/spreadsheets/d/1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/export?format=csv&gid=459543687"

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B",
    "#F6BD16", "#7262FD", "#78D3F8"
]

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    return df

def localizar_coluna(colunas, termos):
    for termo in termos:
        termo_norm = normalizar_texto(termo)
        for coluna in colunas:
            if termo_norm in normalizar_texto(coluna):
                return coluna
    return None

try:
    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO:\n{horario}")

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])

    coluna_data = localizar_coluna(
        colunas,
        [
            "DATA DO EVENTO",
            "DATA EVENTO",
            "DATA_INICIO",
            "DATA INICIO",
            "DATA"
        ]
    )

    if coluna_publico:
        df[coluna_publico] = pd.to_numeric(df[coluna_publico], errors="coerce")

    if coluna_data:
        df[coluna_data] = pd.to_datetime(
            df[coluna_data],
            errors="coerce",
            dayfirst=True
        )

        df = df[df[coluna_data].notna()].copy()

        df = df[
            (df[coluna_data].dt.year >= 2023) &
            (df[coluna_data].dt.year <= 2026)
        ]

        df["Ano"] = df[coluna_data].dt.year.astype("Int64")
        df["Mes_Num"] = df[coluna_data].dt.month.astype("Int64")

        df = df[
            (df["Mes_Num"] >= 1) &
            (df["Mes_Num"] <= 12)
        ]

        mapa_meses = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)

    st.sidebar.subheader("🎯 FILTROS")

    df_filtrado = df.copy()

    if "Ano" in df.columns:
        anos = sorted(df["Ano"].dropna().unique())
        anos_sel = st.sidebar.multiselect("FILTRAR ANO", anos)

        if anos_sel:
            df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_sel)]

    if coluna_comando:
        comandos = sorted(df[coluna_comando].dropna().unique())
        comandos_sel = st.sidebar.multiselect("FILTRAR COMANDO", comandos)

        if comandos_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_comando].isin(comandos_sel)]

    if coluna_cidade:
        cidades = sorted(df[coluna_cidade].dropna().unique())
        cidades_sel = st.sidebar.multiselect("FILTRAR CIDADE", cidades)

        if cidades_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_cidade].isin(cidades_sel)]

    if coluna_natureza:
        natureza = sorted(df[coluna_natureza].dropna().unique())
        natureza_sel = st.sidebar.multiselect("FILTRAR NATUREZA", natureza)

        if natureza_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_natureza].isin(natureza_sel)]

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = len(df_filtrado)
    total_publico = int(df_filtrado[coluna_publico].fillna(0).sum())

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🎉 EVENTOS", total_eventos)
    c2.metric("👥 PÚBLICO", f"{total_publico:,}".replace(",", "."))
    c3.metric("🏙️ CIDADES", df_filtrado[coluna_cidade].nunique())
    c4.metric("🚔 COMANDOS", df_filtrado[coluna_comando].nunique())

    st.subheader("📅 COMPARATIVO ANO/MÊS")

    comparativo = (
        df_filtrado.groupby(["Ano", "Mes_Abrev"])
        .size()
        .reset_index(name="Eventos")
    )

    fig = px.bar(
        comparativo,
        x="Mes_Abrev",
        y="Eventos",
        color="Ano",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=PALETA_BARRAS
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 TOP 10 - PÚBLICO PREVISTO")

    top_publico = (
        df_filtrado.sort_values(
            by=coluna_publico,
            ascending=False
        )
        .head(10)
    )

    st.dataframe(top_publico, use_container_width=True)

    st.subheader("🧠 ANÁLISE INTELIGENTE OPERACIONAL")

    maior_publico = df_filtrado.loc[
        df_filtrado[coluna_publico].idxmax()
    ]

    menor_publico = df_filtrado.loc[
        df_filtrado[coluna_publico].idxmin()
    ]

    media_geral = round(df_filtrado[coluna_publico].mean(), 2)
    mediana = round(df_filtrado[coluna_publico].median(), 2)

    st.info(f"""
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
