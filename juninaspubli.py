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
        letter-spacing: -0.2px;
    }

    .stCaption {
        color: #94A3B8 !important;
        font-size: 0.88rem !important;
    }

    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        padding: 15px;
        border-radius: 12px;
    }

    div[data-testid="metric-container"] label {
        color: white !important;
    }

    div[data-testid="metric-container"] div {
        color: #61DDAA !important;
    }
</style>
""", unsafe_allow_html=True)

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=1866688086"
)

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B", "#F6BD16", "#7262FD",
    "#78D3F8", "#9661BC", "#F6903D", "#008685", "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9", "#61DDAA", "#F6BD16",
    "#7262FD", "#F08BB4", "#78D3F8"
]

COR_HISTOGRAMA = "#9CC3FF"

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode(
        "ASCII", "ignore"
    ).decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)
    df = df.dropna(how="all")
    df.columns = [col.strip() for col in df.columns]
    return df

def localizar_coluna(colunas, termos):
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
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    return df

def tratar_coluna_data(df, coluna):

    if coluna and coluna in df.columns:
        df[coluna] = pd.to_datetime(
            df[coluna],
            errors="coerce",
            dayfirst=True
        )

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
        font=dict(size=13, color="#3B4A5A"),
        bargap=0.22,
        margin=dict(l=20, r=20, t=50, b=20),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor="#D9E2EC",
            tickfont=dict(color="#52606D")
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#EEF2F7",
            zeroline=False,
            linecolor="#D9E2EC",
            tickfont=dict(color="#52606D")
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def preparar_base_eventos(df, coluna_evento):

    if not coluna_evento or coluna_evento not in df.columns:
        return df.copy()

    base = df.copy()

    base["_EVENTO_TEXTO_"] = (
        base[coluna_evento]
        .astype(str)
        .str.strip()
    )

    base = base[base["_EVENTO_TEXTO_"] != ""]

    base = base[
        ~base["_EVENTO_TEXTO_"]
        .str.upper()
        .isin(["NAN", "NONE", "<NA>"])
    ]

    return base

try:

    df = carregar_dados()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(
        f"ÚLTIMA ATUALIZAÇÃO DA CARGA:\n{horario}"
    )

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
        ["PUBLICO", "PUBLICO PREVISTO"]
    )

    coluna_data = localizar_coluna(
        colunas,
        ["DATA"]
    )

    coluna_natureza = localizar_coluna(
        colunas,
        ["NATUREZA"]
    )

    coluna_tipo_publico = localizar_coluna(
        colunas,
        ["TIPO DE PUBLICO", "TIPO PUBLICO"]
    )

    df = tratar_coluna_numerica(df, coluna_publico)
    df = tratar_coluna_data(df, coluna_data)

    df = tratar_coluna_categorica(
        df,
        coluna_tipo_publico
    )

    df = tratar_coluna_categorica(
        df,
        coluna_natureza
    )

    if coluna_data and coluna_data in df.columns:

        df["Ano"] = df[coluna_data].dt.year
        df["Mes_Num"] = df[coluna_data].dt.month

        mapa_meses = {
            1: "Jan", 2: "Fev", 3: "Mar",
            4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set",
            10: "Out", 11: "Nov", 12: "Dez"
        }

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)

        df["AnoMes"] = (
            df["Ano"].astype("Int64").astype(str)
            + "-"
            + df["Mes_Abrev"].fillna("")
        )

        df.loc[df["Ano"].isna(), "AnoMes"] = None

    if "Ano" in df.columns:
        df = df[df["Ano"] != 2022].copy()

    df_historico = preparar_base_eventos(
        df.copy(),
        coluna_evento
    )

    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    if "Ano" in df_filtrado.columns:

        opcoes_ano = sorted(
            df_filtrado["Ano"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            options=opcoes_ano,
            default=[]
        )

        if anos_sel:
            df_filtrado = df_filtrado[
                df_filtrado["Ano"].isin(anos_sel)
            ]

    if coluna_comando:

        opcoes_comando = sorted(
            df_filtrado[coluna_comando]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        comandos_sel = st.sidebar.multiselect(
            "FILTRAR COMANDO",
            options=opcoes_comando,
            default=[]
        )

        if comandos_sel:
            df_filtrado = df_filtrado[
                df_filtrado[coluna_comando]
                .astype(str)
                .isin(comandos_sel)
            ]

    if coluna_cidade:

        opcoes_cidade = sorted(
            df_filtrado[coluna_cidade]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        cidades_sel = st.sidebar.multiselect(
            "FILTRAR CIDADE",
            options=opcoes_cidade,
            default=[]
        )

        if cidades_sel:
            df_filtrado = df_filtrado[
                df_filtrado[coluna_cidade]
                .astype(str)
                .isin(cidades_sel)
            ]

    if coluna_data and df_filtrado[coluna_data].notna().any():

        data_min = df_filtrado[coluna_data].min().date()
        data_max = df_filtrado[coluna_data].max().date()

        intervalo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(intervalo, tuple) and len(intervalo) == 2:

            data_ini, data_fim = intervalo

            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= data_ini)
                &
                (df_filtrado[coluna_data].dt.date <= data_fim)
            ]

    df_filtrado_eventos = preparar_base_eventos(
        df_filtrado.copy(),
        coluna_evento
    )

    st.subheader("📚 PANORAMA GERAL")

    st.caption(
        "OS GRÁFICOS ABAIXO NÃO SOFREM ALTERAÇÃO DOS FILTROS."
    )

    if "Ano" in df_historico.columns:

        st.markdown("### 📊 COMPARATIVO DE EVENTOS POR ANO")

        eventos_ano = (
            df_historico
            .dropna(subset=["Ano"])
            .groupby("Ano")
            .size()
            .reset_index(name="Eventos")
            .sort_values("Ano")
        )

        eventos_ano["Ano"] = (
            eventos_ano["Ano"]
            .astype(int)
            .astype(str)
        )

        fig = px.bar(
            eventos_ano,
            x="Ano",
            y="Eventos",
            color="Ano",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="ANO",
            yaxis_title="EVENTOS"
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if df_filtrado_eventos.empty:

        st.warning(
            "NENHUM REGISTRO ENCONTRADO COM OS FILTROS."
        )

        st.stop()

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = len(df_filtrado_eventos)

    total_publico = (
        int(df_filtrado[coluna_publico].fillna(0).sum())
        if coluna_publico else 0
    )

    total_cidades = (
        df_filtrado[coluna_cidade]
        .nunique()
        if coluna_cidade else 0
    )

    total_comandos = (
        df_filtrado[coluna_comando]
        .nunique()
        if coluna_comando else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🎉 EVENTOS", total_eventos)

    col2.metric(
        "👥 PÚBLICO PREVISTO",
        f"{total_publico:,}".replace(",", ".")
    )

    col3.metric("🏙️ CIDADES", total_cidades)

    col4.metric("🚔 COMANDOS", total_comandos)

    if coluna_natureza:

        st.subheader("🎭 EVENTOS POR NATUREZA")

        natureza_eventos = (
            df_filtrado_eventos
            .dropna(subset=[coluna_natureza])
            .groupby(coluna_natureza)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.pie(
            natureza_eventos,
            names=coluna_natureza,
            values="Eventos",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA
        )

        fig.update_traces(
            textinfo="percent+label"
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if coluna_comando:

        st.subheader("🚔 EVENTOS POR COMANDO")

        comando_eventos = (
            df_filtrado_eventos
            .groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.bar(
            comando_eventos,
            x=coluna_comando,
            y="Eventos",
            color=coluna_comando,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(showlegend=False)

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if coluna_cidade:

        st.subheader("🏙️ CIDADES COM MAIS EVENTOS")

        cidade_eventos = (
            df_filtrado_eventos
            .groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )

        fig = px.bar(
            cidade_eventos,
            x=coluna_cidade,
            y="Eventos",
            color=coluna_cidade,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )

        fig.update_layout(showlegend=False)

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if coluna_publico:

        st.subheader("📊 DISTRIBUIÇÃO DO PÚBLICO")

        fig = px.histogram(
            df_filtrado,
            x=coluna_publico,
            nbins=20
        )

        fig.update_traces(
            marker_color=COR_HISTOGRAMA
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if coluna_data and coluna_publico:

        st.subheader("📈 EVOLUÇÃO DO PÚBLICO")

        evolucao = (
            df_filtrado
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(coluna_data)
        )

        fig = px.line(
            evolucao,
            x=coluna_data,
            y=coluna_publico,
            markers=True
        )

        fig = aplicar_estilo(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("📄 DADOS OPERACIONAIS")

    pesquisa = st.text_input(
        "🔎 PESQUISAR",
        key="pesquisa_final"
    )

    df_tabela = df_filtrado.copy()

    if pesquisa:

        df_tabela = df_tabela[
            df_tabela.astype(str)
            .apply(
                lambda x: x.str.contains(
                    pesquisa,
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        ]

    st.dataframe(
        df_tabela,
        use_container_width=True,
        height=500
    )

    csv = df_tabela.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao_filtrado.csv",
        mime="text/csv"
    )

    st.success(
        f"✅ DASHBOARD ATUALIZADO EM {horario}"
    )

except Exception as erro:

    st.error(
        f"ERRO AO CARREGAR DADOS: {str(erro).upper()}"
    )
