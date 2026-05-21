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
    page_title="OPERAÇÃO SÃO JOÃO 2026",
    page_icon="🚔",
    layout="wide"
)

# =========================================================
# AJUSTE APENAS DO TÍTULO
# =========================================================

st.markdown("""
<div style="
    color: #E5E7EB;
    font-family: inherit;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 0.8rem 0;
    padding: 0;
">
    🚔 OPERAÇÃO SÃO JOÃO 2026
</div>
""", unsafe_allow_html=True)

# =========================================================
# LINK DA PLANILHA
# =========================================================

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1U2re0vGfssfUAFzra2oJoIVp4klRsbkpWBXVXSFd2Rs/"
    "export?format=csv&gid=459543687"
)

# =========================================================
# CORES
# =========================================================

PALETA_BARRAS = [
    "#5B8FF9", "#61DDAA", "#65789B", "#F6BD16",
    "#7262FD", "#78D3F8", "#9661BC", "#F6903D",
    "#008685", "#F08BB4"
]

PALETA_PIZZA = [
    "#5B8FF9", "#61DDAA", "#F6BD16", "#7262FD",
    "#F08BB4", "#78D3F8", "#65789B", "#F6903D",
    "#008685", "#9661BC"
]

COR_LINHA_2 = "#61DDAA"
COR_HISTOGRAMA = "#9CC3FF"

MAPA_MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

# =========================================================
# FUNÇÕES
# =========================================================

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = re.sub(r"\s+", " ", texto)
    return texto

def limpar_categoria(valor):
    if pd.isna(valor):
        return pd.NA
    valor = str(valor).strip()
    if valor == "":
        return pd.NA
    valor = re.sub(r"\s+", " ", valor)
    return valor.upper()

def localizar_coluna(colunas, termos):
    for termo in termos:
        termo_norm = normalizar_texto(termo)
        for coluna in colunas:
            if termo_norm == normalizar_texto(coluna):
                return coluna

    for termo in termos:
        termo_norm = normalizar_texto(termo)
        for coluna in colunas:
            if termo_norm in normalizar_texto(coluna):
                return coluna
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

    s = re.sub(r"[^0-9\.-]", "", s)

    try:
        return float(s)
    except:
        return pd.NA

def parse_data_strict(valor):
    if pd.isna(valor):
        return pd.NaT

    s = str(valor).strip()
    if s in ["", "nan", "None", "0", "0000-00-00", "0000-00-00 00:00:00", "00/00/0000"]:
        return pd.NaT

    s = re.sub(r"\s+", " ", s)

    formatos = [
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formatos:
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except:
            pass

    return pd.NaT

def aplicar_estilo(fig):
    fig.update_layout(
        template="simple_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=13, color="#3B4A5A"),
        bargap=0.22,
        margin=dict(l=20, r=20, t=60, b=30),
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

@st.cache_data(ttl=60)
def carregar_dados():
    df = pd.read_csv(url)
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df

# =========================================================
# INÍCIO
# =========================================================

try:
    df = carregar_dados()
    df_original = df.copy()

    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 DASHBOARD SINCRONIZADO")
    st.sidebar.info(f"ÚLTIMA ATUALIZAÇÃO:\n{horario}")

    colunas = df.columns.tolist()

    coluna_inicio = df.columns[9]   # J
    coluna_fim = df.columns[10]     # K

    coluna_comando = localizar_coluna(colunas, ["COMANDO"])
    coluna_cidade = localizar_coluna(colunas, ["CIDADE", "MUNICIPIO"])
    coluna_evento = localizar_coluna(colunas, ["EVENTO", "NOME EVENTO"])
    coluna_publico = localizar_coluna(colunas, ["PUBLICO", "PÚBLICO", "PUBLICO PREVISTO", "PÚBLICO PREVISTO"])
    coluna_natureza = localizar_coluna(colunas, ["NATUREZA"])
    coluna_tipo_publico = localizar_coluna(colunas, ["TIPO DE PUBLICO", "TIPO DE PÚBLICO", "TIPO PUBLICO"])

    if coluna_publico:
        df[coluna_publico] = df[coluna_publico].apply(converter_numero_misto)
        df[coluna_publico] = pd.to_numeric(df[coluna_publico], errors="coerce")

    df[coluna_inicio] = df[coluna_inicio].apply(parse_data_strict)
    df[coluna_fim] = df[coluna_fim].apply(parse_data_strict)

    if coluna_natureza:
        df[coluna_natureza] = df[coluna_natureza].apply(limpar_categoria)

    if coluna_tipo_publico:
        df[coluna_tipo_publico] = df[coluna_tipo_publico].apply(limpar_categoria)

    if coluna_comando:
        df[coluna_comando] = df[coluna_comando].astype(str).str.strip()

    if coluna_cidade:
        df[coluna_cidade] = df[coluna_cidade].astype(str).str.strip()

    if coluna_evento:
        df[coluna_evento] = df[coluna_evento].astype(str).str.strip()

    df["_ID_LINHA_EVENTO_"] = range(1, len(df) + 1)

    df["DATA_INICIO_BASE"] = df[coluna_inicio]
    df["DATA_FIM_BASE"] = df[coluna_fim]
    df["DATA_EVENTO_BASE"] = df[coluna_inicio]

    total_linhas_original = len(df_original)

    df = df[df["DATA_INICIO_BASE"].notna()].copy()
    df["DATA_FIM_BASE"] = df["DATA_FIM_BASE"].fillna(df["DATA_INICIO_BASE"])
    df.loc[df["DATA_FIM_BASE"] < df["DATA_INICIO_BASE"], "DATA_FIM_BASE"] = df["DATA_INICIO_BASE"]

    df["Ano"] = df["DATA_EVENTO_BASE"].dt.year.astype("Int64")
    df["Mes_Num"] = df["DATA_EVENTO_BASE"].dt.month.astype("Int64")
    df["Mes_Abrev"] = df["Mes_Num"].map(MAPA_MESES)

    df = df[df["Ano"].notna()].copy()
    df = df[df["Ano"] != 2022].copy()

    # =====================================================
    # FILTROS
    # =====================================================

    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 FILTROS")

    anos = sorted(df_filtrado["Ano"].dropna().astype(int).unique().tolist())
    anos_sel = st.sidebar.multiselect("FILTRAR ANO", options=anos, default=[])
    if anos_sel:
        df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_sel)]

    if coluna_comando:
        comandos = sorted(df_filtrado[coluna_comando].dropna().astype(str).unique().tolist())
        comandos_sel = st.sidebar.multiselect("FILTRAR COMANDO", options=comandos, default=[])
        if comandos_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_comando].astype(str).isin(comandos_sel)]

    if coluna_cidade:
        cidades = sorted(df_filtrado[coluna_cidade].dropna().astype(str).unique().tolist())
        cidades_sel = st.sidebar.multiselect("FILTRAR CIDADE", options=cidades, default=[])
        if cidades_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_cidade].astype(str).isin(cidades_sel)]

    if coluna_natureza:
        natureza = sorted(df_filtrado[coluna_natureza].dropna().astype(str).unique().tolist())
        natureza_sel = st.sidebar.multiselect("FILTRAR NATUREZA", options=natureza, default=[])
        if natureza_sel:
            df_filtrado = df_filtrado[df_filtrado[coluna_natureza].astype(str).isin(natureza_sel)]

    if df_filtrado["DATA_INICIO_BASE"].notna().any() and df_filtrado["DATA_FIM_BASE"].notna().any():
        data_min = df_filtrado["DATA_INICIO_BASE"].min().date()
        data_max = df_filtrado["DATA_FIM_BASE"].max().date()

        intervalo = st.sidebar.date_input(
            "FILTRAR PERÍODO",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
            data_ini, data_fim = intervalo
            df_filtrado = df_filtrado[
                (df_filtrado["DATA_INICIO_BASE"].dt.date <= data_fim) &
                (df_filtrado["DATA_FIM_BASE"].dt.date >= data_ini)
            ]

    if df_filtrado.empty:
        st.warning("NENHUM REGISTRO ENCONTRADO.")
        st.stop()

    # =====================================================
    # CONFERÊNCIA DOS DADOS
    # =====================================================

    with st.expander("🔎 CONFERÊNCIA DOS DADOS", expanded=False):
        resumo_ano = (
            df.groupby("Ano")["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values("Ano")
        )

        resumo_meses = (
            df.groupby(["Ano", "Mes_Num", "Mes_Abrev"])["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
        )

        eventos_2026 = int(df[df["Ano"] == 2026]["_ID_LINHA_EVENTO_"].count())
        eventos_jan = int(df[df["Mes_Num"] == 1]["_ID_LINHA_EVENTO_"].count())
        eventos_fev = int(df[df["Mes_Num"] == 2]["_ID_LINHA_EVENTO_"].count())
        descartadas = total_linhas_original - len(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("LINHAS ORIGINAIS", total_linhas_original)
        c2.metric("LINHAS VÁLIDAS EM J", len(df))
        c3.metric("EVENTOS 2026", eventos_2026)
        c4.metric("DESCARTADAS", int(descartadas))

        c5, c6 = st.columns(2)
        c5.metric("EVENTOS EM JANEIRO", eventos_jan)
        c6.metric("EVENTOS EM FEVEREIRO", eventos_fev)

        st.caption(f"Coluna J usada como início: {coluna_inicio}")
        st.caption(f"Coluna K usada como fim: {coluna_fim}")

        st.markdown("### Eventos por ano")
        st.dataframe(resumo_ano, use_container_width=True)

        st.markdown("### Eventos por mês")
        st.dataframe(resumo_meses, use_container_width=True)

    # =====================================================
    # PANORAMA GERAL
    # =====================================================

    st.subheader("📚 PANORAMA GERAL")

    st.markdown("### 📊 COMPARATIVO DE EVENTOS POR ANO")
    eventos_ano = (
        df.groupby("Ano")["_ID_LINHA_EVENTO_"]
        .count()
        .reset_index(name="Eventos")
        .sort_values("Ano")
    )

    eventos_ano["Ano"] = eventos_ano["Ano"].astype(int).astype(str)
    eventos_ano["Eventos_txt"] = eventos_ano["Eventos"].astype(int).astype(str)

    fig_ano = px.bar(
        eventos_ano,
        x="Ano",
        y="Eventos",
        text="Eventos_txt",
        color="Ano",
        color_discrete_sequence=PALETA_BARRAS
    )

    fig_ano.update_traces(textposition="outside")
    fig_ano.update_xaxes(type="category", categoryorder="category ascending")
    fig_ano.update_yaxes(tickformat=",d")
    fig_ano = aplicar_estilo(fig_ano)
    st.plotly_chart(fig_ano, use_container_width=True)

    st.markdown("### 📅 COMPARATIVO ANO/MÊS")
    eventos_mes = (
        df.groupby(["Ano", "Mes_Num", "Mes_Abrev"])["_ID_LINHA_EVENTO_"]
        .count()
        .reset_index(name="Eventos")
        .sort_values(["Ano", "Mes_Num"])
    )
    eventos_mes = eventos_mes[eventos_mes["Eventos"] > 0].copy()
    eventos_mes = eventos_mes[eventos_mes["Mes_Num"].notna()].copy()

    if not eventos_mes.empty:
        meses_existentes = sorted(eventos_mes["Mes_Num"].astype(int).unique().tolist())
        ordem_meses_existentes = [MAPA_MESES[m] for m in meses_existentes if m in MAPA_MESES]

        eventos_mes["Mes_Abrev"] = pd.Categorical(
            eventos_mes["Mes_Abrev"],
            categories=ordem_meses_existentes,
            ordered=True
        )
        eventos_mes["Ano"] = eventos_mes["Ano"].astype(int).astype(str)

        fig_mes = px.bar(
            eventos_mes,
            x="Mes_Abrev",
            y="Eventos",
            color="Ano",
            barmode="group",
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )
        fig_mes.update_xaxes(categoryorder="array", categoryarray=ordem_meses_existentes)
        fig_mes.update_yaxes(tickformat=",d")
        fig_mes = aplicar_estilo(fig_mes)
        st.plotly_chart(fig_mes, use_container_width=True)

    # =====================================================
    # INDICADORES
    # =====================================================

    st.subheader("📌 INDICADORES OPERACIONAIS")

    total_eventos = int(df_filtrado["_ID_LINHA_EVENTO_"].count())
    total_publico = int(df_filtrado[coluna_publico].fillna(0).sum()) if coluna_publico else 0
    total_cidades = df_filtrado[coluna_cidade].dropna().nunique() if coluna_cidade else 0
    total_comandos = df_filtrado[coluna_comando].dropna().nunique() if coluna_comando else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎉 EVENTOS", total_eventos)
    c2.metric("👥 PÚBLICO", f"{total_publico:,}".replace(",", "."))
    c3.metric("🏙️ CIDADES", total_cidades)
    c4.metric("🚔 COMANDOS", total_comandos)

    # =====================================================
    # EVENTOS POR NATUREZA
    # =====================================================

    if coluna_natureza:
        st.subheader("🎭 EVENTOS POR NATUREZA")

        base_natureza = df_filtrado[df_filtrado[coluna_natureza].notna()].copy()

        natureza_df = (
            base_natureza.groupby(coluna_natureza)["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        if not natureza_df.empty:
            fig_nat = px.pie(
                natureza_df,
                names=coluna_natureza,
                values="Eventos",
                hole=0.45,
                color_discrete_sequence=PALETA_PIZZA
            )
            fig_nat.update_traces(
                textinfo="percent+label",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Eventos: %{value}<br>Percentual: %{percent}<extra></extra>"
            )
            fig_nat = aplicar_estilo(fig_nat)
            st.plotly_chart(fig_nat, use_container_width=True)

    # =====================================================
    # EVENTOS POR COMANDO
    # =====================================================

    if coluna_comando:
        st.subheader("🚔 EVENTOS POR COMANDO")

        comando_df = (
            df_filtrado.groupby(coluna_comando)["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.bar(
            comando_df,
            x=coluna_comando,
            y="Eventos",
            color=coluna_comando,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )
        fig.update_yaxes(tickformat=",d")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # CIDADES
    # =====================================================

    if coluna_cidade:
        st.subheader("🏙️ CIDADES COM MAIS EVENTOS")

        cidade_df = (
            df_filtrado.groupby(coluna_cidade)["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )

        fig = px.bar(
            cidade_df,
            x=coluna_cidade,
            y="Eventos",
            color=coluna_cidade,
            text_auto=True,
            color_discrete_sequence=PALETA_BARRAS
        )
        fig.update_yaxes(tickformat=",d")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TOP EVENTOS POR PÚBLICO
    # =====================================================

    if coluna_evento and coluna_publico:
        st.subheader("🎯 EVENTOS COM MAIOR PÚBLICO PREVISTO")

        eventos_publico = (
            df_filtrado
            .dropna(subset=[coluna_evento, coluna_publico])
            .copy()
        )

        eventos_publico[coluna_publico] = pd.to_numeric(
            eventos_publico[coluna_publico], errors="coerce"
        )

        eventos_publico = (
            eventos_publico
            .dropna(subset=[coluna_publico])
            .sort_values(by=coluna_publico, ascending=False)
            .drop_duplicates(subset=[coluna_evento], keep="first")
            .head(10)
            .copy()
        )

        if not eventos_publico.empty:
            eventos_publico["categoria_cor"] = eventos_publico[coluna_evento].astype(str)

            fig = px.bar(
                eventos_publico,
                x=coluna_publico,
                y=coluna_evento,
                orientation="h",
                color="categoria_cor",
                text=coluna_publico,
                color_discrete_sequence=PALETA_BARRAS
            )

            fig.update_traces(textposition="outside")
            fig = aplicar_estilo(fig)

            fig.update_layout(
                showlegend=False,
                xaxis_title="Público Previsto",
                yaxis_title="Evento",
                yaxis=dict(
                    dtick=1,
                    categoryorder="total ascending"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # HISTOGRAMA
    # =====================================================

    if coluna_publico:
        st.subheader("📊 DISTRIBUIÇÃO DO PÚBLICO")

        base_publico = df_filtrado[df_filtrado[coluna_publico].notna()].copy()

        if not base_publico.empty:
            fig = px.histogram(
                base_publico,
                x=coluna_publico,
                nbins=20
            )
            fig.update_traces(marker_color=COR_HISTOGRAMA)
            fig.update_yaxes(tickformat=",d")
            fig = aplicar_estilo(fig)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # EVOLUÇÃO
    # =====================================================

    if coluna_publico and df_filtrado["DATA_EVENTO_BASE"].notna().any():
        st.subheader("📈 EVOLUÇÃO DO PÚBLICO")

        evolucao = (
            df_filtrado.groupby("DATA_EVENTO_BASE")[coluna_publico]
            .sum()
            .reset_index()
            .sort_values("DATA_EVENTO_BASE")
        )

        fig = px.line(
            evolucao,
            x="DATA_EVENTO_BASE",
            y=coluna_publico,
            markers=True
        )
        fig.update_traces(line=dict(color=COR_LINHA_2, width=3))
        fig.update_yaxes(tickformat=",d")
        fig = aplicar_estilo(fig)
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TOP 10
    # =====================================================

    if coluna_publico:
        st.subheader("🔥 TOP 10 - PÚBLICO PREVISTO")

        top_publico = (
            df_filtrado[df_filtrado[coluna_publico].notna()]
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )

        st.dataframe(top_publico, use_container_width=True)

    # =====================================================
    # ANÁLISE INTELIGENTE
    # =====================================================

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

🎉 TOTAL DE EVENTOS:
{total_eventos}

🏙️ TOTAL DE CIDADES:
{total_cidades}

🚔 TOTAL DE COMANDOS:
{total_comandos}
""")

    # =====================================================
    # RANKING OPERACIONAL
    # =====================================================

    if coluna_comando and coluna_publico:
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

        ranking = ranking.sort_values("PÚBLICO TOTAL", ascending=False)
        st.dataframe(ranking, use_container_width=True)

    # =====================================================
    # EVENTOS POR TIPO DE PÚBLICO
    # =====================================================

    if coluna_tipo_publico:
        st.subheader("👥 EVENTOS POR TIPO DE PÚBLICO")

        tipo_publico_df = (
            df_filtrado[df_filtrado[coluna_tipo_publico].notna()]
            .groupby(coluna_tipo_publico)["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        if not tipo_publico_df.empty:
            fig = px.bar(
                tipo_publico_df,
                x=coluna_tipo_publico,
                y="Eventos",
                color=coluna_tipo_publico,
                text_auto=True,
                color_discrete_sequence=PALETA_BARRAS
            )
            fig.update_yaxes(tickformat=",d")
            fig = aplicar_estilo(fig)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # NATUREZA POR COMANDO
    # =====================================================

    if coluna_comando and coluna_natureza:
        st.subheader("🗂️ NATUREZA POR COMANDO")

        nat_comando = (
            df_filtrado[
                df_filtrado[coluna_natureza].notna() &
                df_filtrado[coluna_comando].notna()
            ]
            .groupby([coluna_comando, coluna_natureza])["_ID_LINHA_EVENTO_"]
            .count()
            .reset_index(name="Eventos")
        )

        if not nat_comando.empty:
            fig = px.bar(
                nat_comando,
                x=coluna_comando,
                y="Eventos",
                color=coluna_natureza,
                barmode="stack",
                color_discrete_sequence=PALETA_BARRAS
            )
            fig.update_yaxes(tickformat=",d")
            fig = aplicar_estilo(fig)
            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # TABELA FINAL
    # =====================================================

    st.subheader("📄 DADOS OPERACIONAIS")

    pesquisa = st.text_input("🔎 PESQUISAR NA TABELA")
    tabela = df_filtrado.copy()

    if pesquisa:
        tabela = tabela[
            tabela.astype(str)
            .apply(lambda x: x.str.contains(pesquisa, case=False, na=False))
            .any(axis=1)
        ]

    st.dataframe(tabela, use_container_width=True, height=450)

    # =====================================================
    # DOWNLOAD
    # =====================================================

    csv = tabela.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ BAIXAR CSV",
        data=csv,
        file_name="operacao_sao_joao.csv",
        mime="text/csv"
    )

    st.success(f"✅ DASHBOARD ATUALIZADO EM {horario}")

except Exception as erro:
    st.error(f"ERRO AO CARREGAR DADOS: {str(erro)}")
