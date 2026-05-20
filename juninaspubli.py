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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="titulo-wrap">
    <div class="titulo-linha">🚔 OPERAÇÃO - SÃO JOÃO</div>
    <div class="titulo-linha">2026</div>
    <div class="subtitulo-linha">Painel operacional com panorama histórico fixo e análises filtráveis.</div>
</div>
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
    "#5B8FF9", "#61DDAA", "#F6BD16", "#7262FD", "#F08BB4", "#78D3F8"
]

COR_LINHA_1 = "#5B8FF9"
COR_LINHA_2 = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

MAPA_MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}
ORDEM_MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)
    df = df.dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
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
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df

def tratar_coluna_data(df, coluna):
    if coluna and coluna in df.columns:
        bruto = df[coluna].astype(str).str.strip()

        dt = pd.to_datetime(
            bruto,
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )

        falha = dt.isna() & bruto.ne("") & bruto.ne("nan") & bruto.ne("None") & bruto.ne("<NA>")
        if falha.any():
            dt_fallback = pd.to_datetime(
                bruto[falha],
                dayfirst=True,
                errors="coerce"
            )
            dt.loc[falha] = dt_fallback

        df[coluna] = dt
    return df

def tratar_coluna_categorica(df, coluna):
    if coluna and coluna in df.columns:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.strip()
            .replace(["", "NAN", "None", "none", "nan", "<NA>"], pd.NA)
        )
    return df

def normalizar_cobranca(valor):
    if pd.isna(valor):
        return pd.NA

    txt = normalizar_texto(valor)

    if txt in ["", "NAN", "NONE", "NULL", "NA", "<NA>"]:
        return pd.NA

    mapa_nao = {
        "NAO", "NAO PAGO", "SEM COBRANCA", "SEM COBRANCA DE INGRESSO",
        "GRATUITO", "GRATUITA", "LIVRE", "ISENTO", "ISENTA",
        "FRANQUEADO", "FRANQUEADA", "ENTRADA FRANCA", "SEM PAGAMENTO"
    }

    mapa_sim = {
        "SIM", "COBRADO", "COBRANCA", "PAGO", "PAGA", "PAGAMENTO",
        "INGRESSO PAGO", "COM COBRANCA", "PAGOU", "PAGA ENTRADA",
        "VENDA DE INGRESSO", "COBRANCA DE INGRESSO"
    }

    if txt in mapa_nao:
        return "NÃO"
    if txt in mapa_sim:
        return "SIM"

    if "SEM COBRANCA" in txt or "GRATUIT" in txt or "ENTRADA FRANCA" in txt:
        return "NÃO"
    if "COBRAN" in txt or "PAG" in txt or "INGRESSO" in txt:
        return "SIM"

    return pd.NA

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

try:
    df = carregar_dados()
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO DA CARGA:\n{horario}")

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO", "NOME EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO", "PÚBLICO", "PUBLICO PREVISTO", "PÚBLICO PREVISTO"])
    coluna_inicio = localizar_coluna(colunas, ["INICIO", "INÍCIO", "DATA INICIO", "DATA INÍCIO", "DATA DE INICIO"])
    coluna_fim = localizar_coluna(colunas, ["FIM", "DATA FIM", "DATA DE FIM"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])
    coluna_tipo_publico = localizar_coluna(colunas, ["TIPO DE PUBLICO", "TIPO DE PÚBLICO", "TIPO PUBLICO"])
    coluna_cobranca = localizar_coluna(colunas, ["COBRANCA", "COBRANÇA", "COBRANCA DE INGRESSO", "COBRANÇA DE INGRESSO"])

    df = tratar_coluna_numerica(df, coluna_publico)
    df = tratar_coluna_data(df, coluna_inicio)
    df = tratar_coluna_data(df, coluna_fim)
    df = tratar_coluna_categorica(df, coluna_tipo_publico)
    df = tratar_coluna_categorica(df, coluna_natureza)
    df = tratar_coluna_categorica(df, coluna_cobranca)

    if coluna_cobranca and coluna_cobranca in df.columns:
        df[coluna_cobranca] = df[coluna_cobranca].apply(normalizar_cobranca)

    df["_ID_LINHA_EVENTO_"] = range(1, len(df) + 1)

    df["DATA_INICIO_BASE"] = df[coluna_inicio] if coluna_inicio else pd.NaT
    df["DATA_FIM_BASE"] = df[coluna_fim] if coluna_fim else pd.NaT
    df["DATA_EVENTO_BASE"] = df["DATA_INICIO_BASE"]

    df["Ano"] = df["DATA_EVENTO_BASE"].dt.year
    df["Mes_Num"] = df["DATA_EVENTO_BASE"].dt.month
    df["Mes_Abrev"] = df["Mes_Num"].map(MAPA_MESES)

    df["AnoMes"] = pd.NA
    mask_data_valida = df["DATA_EVENTO_BASE"].notna()
    df.loc[mask_data_valida, "AnoMes"] = (
        df.loc[mask_data_valida, "Ano"].astype(int).astype(str)
        + "-"
        + df.loc[mask_data_valida, "Mes_Abrev"].astype(str)
    )

    df_historico = df.copy()
    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    if "Ano" in df_filtrado.columns and df_filtrado["Ano"].notna().any():
        opcoes_ano = sorted(df_filtrado["Ano"].dropna().astype(int).unique().tolist())
        anos_sel = st.sidebar.multiselect("FILTRAR ANO", options=opcoes_ano, default=[])
        if anos_sel:
            df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_sel)]

    if coluna_comando:
        opcoes_comando = sorted(df_filtrado[coluna_comando].dropna().astype(str).unique().tolist())
        comandos_sel = st.sidebar.multiselect("FILTRAR COMANDO", options=opcoes_comando, default=[])
        if comandos_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_comando].astype(str).isin(comandos_sel)]

    if coluna_cidade:
        opcoes_cidade = sorted(df_filtrado[coluna_cidade].dropna().astype(str).unique().tolist())
        cidades_sel = st.sidebar.multiselect("FILTRAR CIDADE", options=opcoes_cidade, default=[])
        if cidades_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_cidade].astype(str).isin(cidades_sel)]

    if coluna_natureza:
        opcoes_natureza = sorted(df_filtrado[coluna_natureza].dropna().astype(str).unique().tolist())
        natureza_sel = st.sidebar.multiselect("FILTRAR NATUREZA", options=opcoes_natureza, default=[])
        if natureza_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_natureza].astype(str).isin(natureza_sel)]

    if "DATA_INICIO_BASE" in df_filtrado.columns and "DATA_FIM_BASE" in df_filtrado.columns:
        inicio_min = df_filtrado["DATA_INICIO_BASE"].dropna().min() if df_filtrado["DATA_INICIO_BASE"].notna().any() else pd.NaT
        fim_max = df_filtrado["DATA_FIM_BASE"].dropna().max() if df_filtrado["DATA_FIM_BASE"].notna().any() else pd.NaT

        if pd.notna(inicio_min) and pd.notna(fim_max):
            data_base_min = inicio_min.date()
            data_base_max = fim_max.date()

            intervalo = st.sidebar.date_input(
                "FILTRAR PERÍODO",
                value=[data_base_min, data_base_max],
                min_value=data_base_min,
                max_value=data_base_max
            )

            if isinstance(intervalo, (list, tuple)) and len(intervalo) == 2:
                data_ini, data_fim_filtro = intervalo
                if data_ini and data_fim_filtro:
                    df_filtrado = df_filtrado[
                        (
                            df_filtrado["DATA_INICIO_BASE"].dt.date.fillna(data_ini) <= data_fim_filtro
                        ) &
                        (
                            df_filtrado["DATA_FIM_BASE"].dt.date.fillna(data_fim_filtro) >= data_ini
                        )
                    ]

    st.subheader("📚 PANORAMA GERAL")
    st.caption("OS GRÁFICOS ABAIXO PERMANECEM FIXOS E NÃO SÃO ALTERADOS PELOS FILTROS OPERACIONAIS DA BARRA LATERAL.")

    # Conferência de parsing
    with st.expander("🔎 Conferência de datas", expanded=False):
        total_linhas = len(df)
        linhas_inicio_valido = int(df["DATA_EVENTO_BASE"].notna().sum())
        linhas_2026 = int((df["Ano"] == 2026).sum())
        linhas_inicio_nulo = int(df["DATA_EVENTO_BASE"].isna().sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de linhas", total_linhas)
        c2.metric("INICIO válido", linhas_inicio_valido)
        c3.metric("Ano 2026", linhas_2026)
        c4.metric("INICIO inválido", linhas_inicio_nulo)

        if coluna_inicio:
            amostra_invalidas = df[df["DATA_EVENTO_BASE"].isna()].copy()
            cols_show = [col for col in [coluna_inicio, coluna_fim, coluna_evento, coluna_cidade, coluna_comando] if col]
            if not amostra_invalidas.empty and cols_show:
                st.dataframe(amostra_invalidas[cols_show].head(50), use_container_width=True)

    if "Ano" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📊 COMPARATIVO DE EVENTOS POR ANO")
        eventos_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")["_ID_LINHA_EVENTO_"]
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
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="ANO", yaxis_title="EVENTOS", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "Ano" in df_historico.columns and coluna_publico and df_historico["Ano"].notna().any():
        st.markdown("### 👥 PÚBLICO PREVISTO POR ANO")
        publico_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")[coluna_publico]
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
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="ANO", yaxis_title="PÚBLICO PREVISTO", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "DATA_EVENTO_BASE" in df_historico.columns and df_historico["DATA_EVENTO_BASE"].notna().any():
        st.markdown("### 📅 COMPARATIVO DE EVENTOS POR MÊS E ANO")
        base_mes = df_historico[df_historico["DATA_EVENTO_BASE"].notna()].copy()

        eventos_mes_ano = (
            base_mes.groupby(["Ano", "Mes_Num", "Mes_Abrev"])["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
        )

        eventos_mes_ano["Mes_Abrev"] = pd.Categorical(
            eventos_mes_ano["Mes_Abrev"],
            categories=ORDEM_MESES,
            ordered=True
        )
        eventos_mes_ano["Ano"] = eventos_mes_ano["Ano"].astype(int).astype(str)

        fig = px.bar(
            eventos_mes_ano,
            x="Mes_Abrev",
            y="Eventos",
            color="Ano",
            barmode="group",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(xaxis_title="MÊS", yaxis_title="EVENTOS", legend_title="ANO")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if "AnoMes" in df_historico.columns and df_historico["AnoMes"].notna().any():
        st.markdown("### 📌 EVENTOS POR ANO-MÊS")

        ordem_anomes = (
            df_historico.dropna(subset=["Ano", "Mes_Num", "AnoMes"])
            [["Ano", "Mes_Num", "AnoMes"]]
            .drop_duplicates()
            .sort_values(["Ano", "Mes_Num"])["AnoMes"]
            .tolist()
        )

        eventos_anomes = (
            df_historico.dropna(subset=["AnoMes"])
            .groupby("AnoMes")["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
        )

        eventos_anomes["AnoMes"] = pd.Categorical(
            eventos_anomes["AnoMes"],
            categories=ordem_anomes,
            ordered=True
        )
        eventos_anomes = eventos_anomes.sort_values("AnoMes")

        fig = px.bar(
            eventos_anomes,
            x="AnoMes",
            y="Eventos",
            color="Eventos",
            text_auto=True,
            color_continuous_scale="Blues",
            template="simple_white"
        )
        fig.update_layout(
            xaxis_title="ANO-MÊS",
            yaxis_title="EVENTOS",
            coloraxis_showscale=False
        )
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if df_filtrado.empty:
        st.warning("NENHUM REGISTRO ENCONTRADO COM OS FILTROS APLICADOS.")
        st.stop()

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = int(df_filtrado["_ID_LINHA_EVENTO_"].count())
    total_publico = int(df_filtrado[coluna_publico].fillna(0).sum()) if coluna_publico and coluna_publico in df_filtrado.columns else 0
    total_cidades = (
        df_filtrado[coluna_cidade].dropna().astype(str).apply(normalizar_texto).nunique()
        if coluna_cidade and coluna_cidade in df_filtrado.columns else 0
    )
    total_comandos = (
        df_filtrado[coluna_comando].dropna().astype(str).apply(normalizar_texto).nunique()
        if coluna_comando and coluna_comando in df_filtrado.columns else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎉 EVENTOS", total_eventos)
    col2.metric("👥 PÚBLICO PREVISTO", f"{total_publico:,}".replace(",", "."))
    col3.metric("🏙️ CIDADES", total_cidades)
    col4.metric("🚔 COMANDOS", total_comandos)

except Exception as erro:
    st.error(f"ERRO AO CARREGAR DADOS: {str(erro).upper()}")
