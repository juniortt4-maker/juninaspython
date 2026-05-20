import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
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
    "#5B8FF9", "#61DDAA", "#F6BD16", "#7262FD", "#F08BB4", "#78D3F8"
]

COR_BARRA_UNICA = "#5B8FF9"
COR_LINHA_1 = "#5B8FF9"
COR_LINHA_2 = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

def caixa_alta(texto):
    return str(texto).upper()

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
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
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce", dayfirst=True)
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

def preparar_base_eventos(df, coluna_evento):
    if not coluna_evento or coluna_evento not in df.columns:
        return df.copy()

    base = df.copy()
    base["_EVENTO_TEXTO_"] = base[coluna_evento].astype(str).str.strip()
    base = base[base["_EVENTO_TEXTO_"] != ""]
    base = base[~base["_EVENTO_TEXTO_"].str.upper().isin(["NAN", "NONE", "<NA>"])]
    return base

try:
    df = carregar_dados()
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO DA CARGA:\n{horario}")

    colunas = df.columns.tolist()

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO", "NOME EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO", "PUBLICO PREVISTO"])
    coluna_data = localizar_coluna(colunas, ["DATA"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])
    coluna_tipo_publico = localizar_coluna(colunas, ["TIPO DE PUBLICO", "TIPO PUBLICO"])
    coluna_cobranca = colunas[19] if len(colunas) > 19 else None

    df = tratar_coluna_numerica(df, coluna_publico)
    df = tratar_coluna_data(df, coluna_data)
    df = tratar_coluna_categorica(df, coluna_tipo_publico)
    df = tratar_coluna_categorica(df, coluna_natureza)
    df = tratar_coluna_categorica(df, coluna_cobranca)

    if coluna_cobranca and coluna_cobranca in df.columns:
        df[coluna_cobranca] = df[coluna_cobranca].apply(normalizar_cobranca)

    if coluna_data and coluna_data in df.columns:
        df["Ano"] = df[coluna_data].dt.year
        df["Mes_Num"] = df[coluna_data].dt.month

        mapa_meses = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)
        df["AnoMes"] = df["Ano"].astype("Int64").astype(str) + "-" + df["Mes_Abrev"].fillna("")
        df.loc[df["Ano"].isna(), "AnoMes"] = None

    if "Ano" in df.columns:
        df = df[df["Ano"] != 2022].copy()

    df_historico = preparar_base_eventos(df.copy(), coluna_evento)
    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    if "Ano" in df_filtrado.columns and df_filtrado["Ano"].notna().any():
        opcoes_ano = sorted(df_filtrado["Ano"].dropna().astype(int).unique().tolist())
        anos_sel = st.sidebar.multiselect(
            "FILTRAR ANO",
            options=opcoes_ano,
            default=[]
        )
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

    if coluna_data and df_filtrado[coluna_data].notna().any():
        data_base_min = df_filtrado[coluna_data].min().date()
        data_base_max = df_filtrado[coluna_data].max().date()

        intervalo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_base_min, data_base_max),
            min_value=data_base_min,
            max_value=data_base_max
        )

        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_ini, data_fim = intervalo
            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= data_ini) &
                (df_filtrado[coluna_data].dt.date <= data_fim)
            ]

    df_filtrado_eventos = preparar_base_eventos(df_filtrado.copy(), coluna_evento)

    st.subheader("📚 PANORAMA GERAL")
    st.caption("OS GRÁFICOS ABAIXO PERMANECEM FIXOS E NÃO SÃO ALTERADOS PELOS FILTROS OPERACIONAIS DA BARRA LATERAL.")

    if "Ano" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📊 COMPARATIVO DE EVENTOS POR ANO")
        eventos_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")
            .size()
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

    if "Ano" in df_historico.columns and "Mes_Num" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📅 COMPARATIVO DE EVENTOS POR MÊS E ANO")
        eventos_mes_ano = (
            df_historico.dropna(subset=["Ano", "Mes_Num", "Mes_Abrev"])
            .groupby(["Ano", "Mes_Num", "Mes_Abrev"])
            .size()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
        )

        ordem_meses_abrev = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        eventos_mes_ano["Mes_Abrev"] = pd.Categorical(
            eventos_mes_ano["Mes_Abrev"],
            categories=ordem_meses_abrev,
            ordered=True
        )
        eventos_mes_ano["Ano"] = eventos_mes_ano["Ano"].astype(int).astype(str)
        eventos_mes_ano = eventos_mes_ano.sort_values(["Ano", "Mes_Num"])

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
            .groupby("AnoMes")
            .size()
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

    if df_filtrado_eventos.empty:
        st.warning("NENHUM REGISTRO ENCONTRADO COM OS FILTROS APLICADOS.")
        st.stop()

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = len(df_filtrado_eventos)
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

    if coluna_natureza:
        st.subheader("🎭 EVENTOS POR NATUREZA")
        natureza_eventos = (
            df_filtrado_eventos.dropna(subset=[coluna_natureza])
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
            color_discrete_sequence=PALETA_PIZZA,
            template="simple_white"
        )
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="white", width=2)))
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_tipo_publico:
        st.subheader("🥧 TIPO DE PÚBLICO")
        pizza_publico = (
            df_filtrado.dropna(subset=[coluna_tipo_publico])
            .groupby(coluna_tipo_publico)
            .size()
            .reset_index(name="Quantidade")
            .sort_values(by="Quantidade", ascending=False)
        )
        fig = px.pie(
            pizza_publico,
            names=coluna_tipo_publico,
            values="Quantidade",
            hole=0.45,
            color_discrete_sequence=PALETA_PIZZA,
            template="simple_white"
        )
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="white", width=2)))
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_comando:
        st.subheader("🚔 EVENTOS POR COMANDO")
        comando_eventos = (
            df_filtrado_eventos.dropna(subset=[coluna_comando])
            .groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )
        comando_eventos["categoria_cor"] = comando_eventos[coluna_comando].astype(str)

        fig = px.bar(
            comando_eventos,
            x=coluna_comando,
            y="Eventos",
            color="categoria_cor",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False, xaxis_title="COMANDO", yaxis_title="EVENTOS")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade:
        st.subheader("🏙️ CIDADES COM MAIS EVENTOS")
        cidade_eventos = (
            df_filtrado_eventos.dropna(subset=[coluna_cidade])
            .groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )
        cidade_eventos["categoria_cor"] = cidade_eventos[coluna_cidade].astype(str)

        fig = px.bar(
            cidade_eventos,
            x=coluna_cidade,
            y="Eventos",
            color="categoria_cor",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False, xaxis_title="CIDADE", yaxis_title="EVENTOS")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_evento and coluna_publico:
        st.subheader("🎯 EVENTOS COM MAIOR PÚBLICO PREVISTO")
        eventos_publico = (
            df_filtrado_eventos.dropna(subset=[coluna_evento])
            .groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )
        eventos_publico["categoria_cor"] = eventos_publico[coluna_evento].astype(str)

        fig = px.bar(
            eventos_publico,
            x=coluna_evento,
            y=coluna_publico,
            color="categoria_cor",
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False, xaxis_title="EVENTO", yaxis_title="PÚBLICO PREVISTO")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("📊 DISTRIBUIÇÃO DO PÚBLICO PREVISTO")
        fig = px.histogram(df_filtrado, x=coluna_publico, nbins=20, template="simple_white")
        fig.update_traces(marker_color=COR_HISTOGRAMA, marker_line_color="white", marker_line_width=1)
        fig.update_layout(xaxis_title="PÚBLICO PREVISTO", yaxis_title="FREQUÊNCIA", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_comando and coluna_publico:
        st.subheader("🚔 PÚBLICO PREVISTO POR COMANDO")
        publico_comando = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
        )
        publico_comando["categoria_cor"] = publico_comando[coluna_comando].astype(str)

        fig = px.bar(
            publico_comando,
            x=coluna_comando,
            y=coluna_publico,
            color="categoria_cor",
            text_auto=".2s",
            color_discrete_sequence=PALETA_BARRAS,
            template="simple_white"
        )
        fig.update_layout(showlegend=False, xaxis_title="COMANDO", yaxis_title="PÚBLICO PREVISTO")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)



    if coluna_cidade and coluna_publico:
        st.subheader("📈 MÉDIA DE PÚBLICO POR CIDADE")
        media_cidade = (
            df_filtrado.groupby(coluna_cidade)[coluna_publico]
            .mean()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(15)
        )
        fig = px.line(media_cidade, x=coluna_cidade, y=coluna_publico, markers=True, template="simple_white")
        fig.update_traces(line=dict(color=COR_LINHA_1, width=3), marker=dict(size=8, color=COR_LINHA_1))
        fig.update_layout(xaxis_title="CIDADE", yaxis_title="MÉDIA DE PÚBLICO", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌡️ INTENSIDADE DE PÚBLICO POR CIDADE")
        mapa_df = (
            df_filtrado[[coluna_cidade, coluna_publico]]
            .dropna()
            .groupby(coluna_cidade)[coluna_publico]
            .sum()
            .reset_index()
        )

        fig_heat = go.Figure(
            data=go.Heatmap(
                z=[mapa_df[coluna_publico].tolist()],
                x=mapa_df[coluna_cidade].astype(str).tolist(),
                y=["PÚBLICO"],
                colorscale="Blues"
            )
        )
        fig_heat.update_layout(template="simple_white", height=450, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    if coluna_data and coluna_publico and df_filtrado[coluna_data].notna().any():
        st.subheader("📈 EVOLUÇÃO DO PÚBLICO")
        evolucao = (
            df_filtrado.dropna(subset=[coluna_data])
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(coluna_data)
        )
        fig = px.line(evolucao, x=coluna_data, y=coluna_publico, markers=True, template="simple_white")
        fig.update_traces(line=dict(color=COR_LINHA_2, width=3), marker=dict(size=8, color=COR_LINHA_2))
        fig.update_layout(xaxis_title="DATA", yaxis_title="PÚBLICO PREVISTO", showlegend=False)
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("🔥 TOP 10 - PÚBLICO PREVISTO")
        top_publico = df_filtrado.sort_values(by=coluna_publico, ascending=False).head(10)
        st.dataframe(top_publico, use_container_width=True)

    st.subheader("🧠 ANÁLISE INTELIGENTE OPERACIONAL")

    if coluna_publico and not df_filtrado[coluna_publico].dropna().empty:
        maior_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmax()]
        menor_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmin()]
        media_geral = round(df_filtrado[coluna_publico].mean(), 2)
        mediana = round(df_filtrado[coluna_publico].median(), 2)

        nome_maior = maior_publico[coluna_evento] if coluna_evento else "N/D"
        nome_menor = menor_publico[coluna_evento] if coluna_evento else "N/D"

        st.info(f"""
🚨 EVENTO COM MAIOR PÚBLICO PREVISTO:
{str(nome_maior).upper()} ({int(maior_publico[coluna_publico]):,} PESSOAS)

⚠️ EVENTO COM MENOR PÚBLICO PREVISTO:
{str(nome_menor).upper()} ({int(menor_publico[coluna_publico]):,} PESSOAS)

📊 MÉDIA GERAL DE PÚBLICO:
{media_geral:,.0f} PESSOAS

📈 MEDIANA DE PÚBLICO:
{mediana:,.0f} PESSOAS

🎉 TOTAL DE EVENTOS MONITORADOS:
{total_eventos}

🏙️ TOTAL DE CIDADES:
{df_filtrado[coluna_cidade].nunique() if coluna_cidade else 0}

🚔 TOTAL DE COMANDOS:
{df_filtrado[coluna_comando].nunique() if coluna_comando else 0}
""")

    if coluna_comando and coluna_publico:
        st.subheader("🏆 RANKING OPERACIONAL DOS COMANDOS")
        ranking_operacional = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )
        ranking_operacional.columns = ["COMANDO", "PÚBLICO TOTAL", "MÉDIA PÚBLICO", "REGISTROS"]
        st.dataframe(ranking_operacional, use_container_width=True)

    st.subheader("📄 DADOS OPERACIONAIS")
    pesquisa_final = st.text_input("🔎 PESQUISAR NA TABELA FINAL", key="pesquisa_final")

    df_tabela = df_filtrado.copy()
    if pesquisa_final:
        df_tabela = df_tabela[
            df_tabela.astype(str)
            .apply(lambda x: x.str.contains(pesquisa_final, case=False, na=False))
            .any(axis=1)
        ]

    st.dataframe(df_tabela, use_container_width=True, height=450)

    csv = df_tabela.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao_filtrado.csv",
        mime="text/csv"
    )

    st.success(f"✅ DASHBOARD ATUALIZADO EM {horario}")

except Exception as erro:
    st.error(f"ERRO AO CARREGAR DADOS: {str(erro).upper()}")
