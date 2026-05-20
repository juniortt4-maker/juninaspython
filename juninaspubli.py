import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import unicodedata
import re

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="OPERAÇÃO - SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

    .stApp {
        background: #0B0F14;
    }

    .block-container {
        padding-top: 0.25rem;
        max-width: 100%;
    }

    .titulo-wrap {
        display: block;
        width: 100%;
        overflow: visible !important;
        padding-bottom: 0.45rem;
        margin-bottom: 0.25rem;
    }

    .titulo-linha {
        display: block;
        width: 100%;
        color: #E5E7EB;
        font-size: clamp(1.00rem, 1.8vw, 1.70rem);
        font-weight: 800;
        line-height: 1.38 !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
        overflow: visible !important;
    }

    .subtitulo-linha {
        display: block;
        width: 100%;
        color: #94A3B8;
        font-size: 0.92rem;
        line-height: 1.45;
        margin-top: 0.12rem;
        white-space: normal !important;
    }

    h1, h2, h3 {
        color: #E5E7EB;
        letter-spacing: -0.2px;
    }

    .stCaption {
        color: #94A3B8 !important;
        font-size: 0.88rem !important;
    }

    .kpi-card {
        background: #111827;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #1F2937;
        box-shadow: 0 0 10px rgba(0,0,0,0.15);
    }

    .kpi-titulo {
        color: #9CA3AF;
        font-size: 14px;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .kpi-valor {
        color: white;
        font-size: 34px;
        font-weight: 800;
    }

</style>
""", unsafe_allow_html=True)

# =========================================================
# TÍTULO
# =========================================================

st.markdown("""
<div class="titulo-wrap">
    <div class="titulo-linha">🚔 OPERAÇÃO - SÃO JOÃO</div>
    <div class="titulo-linha">2026</div>
    <div class="subtitulo-linha">
        Painel operacional com panorama histórico fixo e análises filtráveis.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# URL GOOGLE SHEETS
# =========================================================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=1866688086"
)

# =========================================================
# PALETAS
# =========================================================

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B", "#F6BD16",
    "#7262FD", "#78D3F8", "#9661BC", "#F6903D"
]

MAPA_MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

ORDEM_MESES = [
    "Jan", "Fev", "Mar", "Abr",
    "Mai", "Jun", "Jul", "Ago",
    "Set", "Out", "Nov", "Dez"
]

# =========================================================
# FUNÇÕES
# =========================================================

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize(
        "NFKD", texto
    ).encode(
        "ASCII", "ignore"
    ).decode("utf-8")

    texto = re.sub(r"\s+", " ", texto)
    return texto


@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)

    df = df.dropna(how="all")

    df.columns = [str(c).strip() for c in df.columns]

    return df


def localizar_coluna(colunas, termos):

    for termo in termos:
        termo_norm = normalizar_texto(termo)

        for c in colunas:
            if termo_norm == normalizar_texto(c):
                return c

    for termo in termos:
        termo_norm = normalizar_texto(termo)

        for c in colunas:
            if termo_norm in normalizar_texto(c):
                return c

    return None


def converter_numero_misto(valor):

    if pd.isna(valor):
        return pd.NA

    s = str(valor).strip()

    if s == "":
        return pd.NA

    s = s.replace(" ", "")
    s = re.sub(r"[R$\u00A0]", "", s)

    if "," in s and "." in s:

        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

    elif "," in s:
        s = s.replace(".", "")
        s = s.replace(",", ".")

    else:
        s = s.replace(",", "")

    s = re.sub(r"[^0-9\\.-]", "", s)

    try:
        return float(s)

    except:
        return pd.NA


def tratar_coluna_numerica(df, coluna):

    if coluna and coluna in df.columns:

        df[coluna] = df[coluna].apply(converter_numero_misto)

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    return df


def tratar_coluna_data(df, coluna):

    if coluna and coluna in df.columns:

        bruto = df[coluna].astype(str).str.strip()

        dt = pd.to_datetime(
            bruto,
            dayfirst=True,
            errors="coerce"
        )

        df[coluna] = dt

    return df


def tratar_coluna_categorica(df, coluna):

    if coluna and coluna in df.columns:

        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.strip()
            .replace(
                ["", "NAN", "None", "none", "nan", "<NA>"],
                pd.NA
            )
        )

    return df


def aplicar_estilo(fig):

    fig.update_layout(

        template="simple_white",

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            size=13,
            color="#3B4A5A"
        ),

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Arial"
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#D9E2EC"
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#EEF2F7",
            zeroline=False,
            linecolor="#D9E2EC"
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )

    )

    return fig

# =========================================================
# CARREGAMENTO
# =========================================================

try:

    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO:\n{horario}")

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(
        colunas,
        ["COMANDO"]
    )

    coluna_cidade = localizar_coluna(
        colunas,
        ["CIDADE", "MUNICIPIO"]
    )

    coluna_evento = localizar_coluna(
        colunas,
        ["EVENTO", "NOME EVENTO"]
    )

    coluna_publico = localizar_coluna(
        colunas,
        ["PUBLICO", "PÚBLICO"]
    )

    coluna_inicio = localizar_coluna(
        colunas,
        ["INICIO", "INÍCIO", "DATA INICIO"]
    )

    coluna_fim = localizar_coluna(
        colunas,
        ["FIM", "DATA FIM"]
    )

    coluna_natureza = localizar_coluna(
        colunas,
        ["NATUREZA"]
    )

    # =====================================================
    # TRATAMENTOS
    # =====================================================

    if not coluna_publico:
        df["PUBLICO_PADRAO"] = 0
        coluna_publico = "PUBLICO_PADRAO"

    df = tratar_coluna_numerica(df, coluna_publico)

    df = tratar_coluna_data(df, coluna_inicio)

    df = tratar_coluna_data(df, coluna_fim)

    df = tratar_coluna_categorica(df, coluna_natureza)

    # =====================================================
    # BASES DE DATAS
    # =====================================================

    df["DATA_INICIO_BASE"] = (
        df[coluna_inicio]
        if coluna_inicio and coluna_inicio in df.columns
        else pd.Series(pd.NaT, index=df.index)
    )

    df["DATA_FIM_BASE"] = (
        df[coluna_fim]
        if coluna_fim and coluna_fim in df.columns
        else pd.Series(pd.NaT, index=df.index)
    )

    df["DATA_EVENTO_BASE"] = df["DATA_INICIO_BASE"]

    df["_ID_LINHA_EVENTO_"] = range(1, len(df) + 1)

    # =====================================================
    # CAMPOS DE TEMPO
    # =====================================================

    df["Ano"] = df["DATA_EVENTO_BASE"].dt.year

    df["Mes_Num"] = df["DATA_EVENTO_BASE"].dt.month

    df["Mes_Abrev"] = df["Mes_Num"].map(MAPA_MESES)

    # =====================================================
    # FILTROS
    # =====================================================

    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    if df["Ano"].notna().any():

        anos = sorted(
            df["Ano"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            anos
        )

        if anos_sel:
            df_filtrado = df_filtrado[
                df_filtrado["Ano"].isin(anos_sel)
            ]

    if coluna_comando:

        comandos = sorted(
            df_filtrado[coluna_comando]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        comandos_sel = st.sidebar.multiselect(
            "FILTRAR COMANDO",
            comandos
        )

        if comandos_sel:
            df_filtrado = df_filtrado[
                df_filtrado[coluna_comando]
                .astype(str)
                .isin(comandos_sel)
            ]

    if coluna_cidade:

        cidades = sorted(
            df_filtrado[coluna_cidade]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        cidades_sel = st.sidebar.multiselect(
            "FILTRAR CIDADE",
            cidades
        )

        if cidades_sel:
            df_filtrado = df_filtrado[
                df_filtrado[coluna_cidade]
                .astype(str)
                .isin(cidades_sel)
            ]

    # =====================================================
    # KPIS
    # =====================================================

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = int(
        df_filtrado["_ID_LINHA_EVENTO_"].count()
    )

    total_publico = int(
        df_filtrado[coluna_publico]
        .fillna(0)
        .sum()
    )

    total_cidades = (
        df_filtrado[coluna_cidade]
        .dropna()
        .nunique()
        if coluna_cidade else 0
    )

    total_comandos = (
        df_filtrado[coluna_comando]
        .dropna()
        .nunique()
        if coluna_comando else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-titulo">🎉 EVENTOS</div>
            <div class="kpi-valor">{total_eventos}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-titulo">👥 PÚBLICO</div>
            <div class="kpi-valor">
                {total_publico:,}
            </div>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-titulo">🏙️ CIDADES</div>
            <div class="kpi-valor">{total_cidades}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-titulo">🚔 COMANDOS</div>
            <div class="kpi-valor">{total_comandos}</div>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # EVENTOS POR ANO
    # =====================================================

    st.markdown("## 📊 EVENTOS POR ANO")

    eventos_ano = (
        df.groupby("Ano")["_ID_LINHA_EVENTO_"]
        .count()
        .reset_index(name="Eventos")
        .sort_values("Ano")
    )

    eventos_ano["Ano"] = eventos_ano["Ano"].astype(int).astype(str)

    fig = px.bar(
        eventos_ano,
        x="Ano",
        y="Eventos",
        color="Ano",
        text_auto=True,
        color_discrete_sequence=PALETA_BARRAS
    )

    fig = aplicar_estilo(fig)

    fig.update_layout(
        showlegend=False,
        xaxis_title="ANO",
        yaxis_title="EVENTOS"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # =====================================================
    # PÚBLICO POR ANO
    # =====================================================

    st.markdown("## 👥 PÚBLICO PREVISTO POR ANO")

    publico_ano = (
        df.groupby("Ano")[coluna_publico]
        .sum()
        .reset_index()
        .sort_values("Ano")
    )

    publico_ano["Ano"] = publico_ano["Ano"].astype(int).astype(str)

    fig = px.bar(
        publico_ano,
        x="Ano",
        y=coluna_publico,
        color="Ano",
        text_auto=".2s",
        color_discrete_sequence=PALETA_BARRAS
    )

    fig = aplicar_estilo(fig)

    fig.update_layout(
        showlegend=False,
        xaxis_title="ANO",
        yaxis_title="PÚBLICO"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # =====================================================
    # TOP CIDADES
    # =====================================================

    if coluna_cidade:

        st.markdown("## 🏙️ TOP 10 CIDADES")

        top_cidades = (
            df_filtrado
            .groupby(coluna_cidade)["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values("Eventos", ascending=False)
            .head(10)
        )

        fig = px.bar(
            top_cidades,
            x="Eventos",
            y=coluna_cidade,
            orientation="h",
            text_auto=True,
            color="Eventos",
            color_continuous_scale="Blues"
        )

        fig = aplicar_estilo(fig)

        fig.update_layout(
            yaxis_title="",
            xaxis_title="EVENTOS",
            coloraxis_showscale=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # =====================================================
    # EVENTOS POR MÊS
    # =====================================================

    st.markdown("## 📅 EVENTOS POR MÊS")

    eventos_mes = (
        df.groupby("Mes_Abrev")["_ID_LINHA_EVENTO_"]
        .count()
        .reset_index(name="Eventos")
    )

    eventos_mes["Mes_Abrev"] = pd.Categorical(
        eventos_mes["Mes_Abrev"],
        categories=ORDEM_MESES,
        ordered=True
    )

    eventos_mes = eventos_mes.sort_values("Mes_Abrev")

    fig = px.line(
        eventos_mes,
        x="Mes_Abrev",
        y="Eventos",
        markers=True
    )

    fig = aplicar_estilo(fig)

    fig.update_traces(
        line=dict(width=4)
    )

    fig.update_layout(
        xaxis_title="MÊS",
        yaxis_title="EVENTOS"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # =====================================================
    # TABELA
    # =====================================================

    st.markdown("## 📋 BASE OPERACIONAL")

    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=500
    )

except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro)}"
    )
