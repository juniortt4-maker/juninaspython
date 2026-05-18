import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import unicodedata

st.set_page_config(
    page_title="Dashboard Operacional - Festas Juninas",
    page_icon="🚔",
    layout="wide"
)

st.title("🚔 DASHBOARD OPERACIONAL - FESTAS JUNINAS")

st_autorefresh(interval=15000, key="refresh_dashboard")

url = (
    "https://docs.google.com/spreadsheets/d/"
    "1qQrvomIDols1qLFsziiCP2BZtXLRXpjsErXKqONTsVE/"
    "export?format=csv&gid=1996198248"
)

FUNDO_PRETO = "#0E1117"

PALETA_GRAFICO_1 = ["#48CAE4", "#ADE8F4"]  # azul/ciano mais claro
PALETA_GRAFICO_2 = ["#F6BD60", "#F7C59F"]  # dourado/laranja mais claro
PALETA_GRAFICO_3 = ["#52B788", "#95D5B2"]  # verde mais claro
PALETA_GRAFICO_4 = ["#C77DFF", "#E0AAFF"]  # roxo/lilás mais claro

def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    return texto

@st.cache_data(ttl=10)
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

def tratar_coluna_numerica(df, coluna):
    if coluna and coluna in df.columns:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )
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
            .replace(["", "NAN", "None", "none", "nan"], pd.NA)
        )
    return df

def classificar_cobranca(valor):
    if pd.isna(valor):
        return "NÃO INFORMADO"

    texto = normalizar_texto(valor)

    if texto in ["", "NAN", "NONE", "NULL", "NA"]:
        return "NÃO INFORMADO"

    termos_nao = {
        "NAO", "NÃO", "SEM COBRANCA", "SEM COBRANÇA", "GRATUITO", "GRATUITA",
        "LIVRE", "FRANQUEADO", "ISENTO", "ISENTA", "ENTRADA FRANCA",
        "ACESSO LIVRE", "SEM PAGAMENTO", "NAO COBRA", "NAO PAGO"
    }

    termos_sim = {
        "SIM", "COBRADO", "COBRANCA", "COBRANÇA", "PAGO", "PAGA",
        "PAGAMENTO", "INGRESSO PAGO", "COM COBRANCA", "COM COBRANÇA",
        "COBRA", "PAGANTE", "BILHETERIA"
    }

    if texto in termos_nao:
        return "NÃO"

    if texto in termos_sim:
        return "SIM"

    if "SEM COBRAN" in texto or "GRATUIT" in texto or "ISENT" in texto or "LIVRE" in texto:
        return "NÃO"

    if "COBRAN" in texto or "PAG" in texto or "INGRESSO" in texto or "BILHETERIA" in texto:
        return "SIM"

    return "NÃO INFORMADO"

def formatar_milhares(valor):
    if pd.isna(valor):
        return "0"
    return f"{int(round(valor)):,}".replace(",", ".")

def gerar_cores_alternadas(qtd, paleta):
    return [paleta[i % len(paleta)] for i in range(qtd)]

def aplicar_layout_escuro(fig, xaxis_title="", yaxis_title="", showlegend=False, legend_title=None):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor=FUNDO_PRETO,
        paper_bgcolor=FUNDO_PRETO,
        font=dict(color="white"),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=showlegend,
        legend_title=legend_title
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.10)")
    return fig

try:
    df = carregar_dados()
    horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.success("🟢 Dashboard sincronizado")
    st.sidebar.info(f"Atualização automática ativa\n\nÚltima atualização:\n{horario}")

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

    if coluna_data and coluna_data in df.columns:
        df = df[df[coluna_data].notna()].copy()

        df["Ano"] = df[coluna_data].dt.year
        df["Mes_Num"] = df[coluna_data].dt.month

        df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
        df["Mes_Num"] = pd.to_numeric(df["Mes_Num"], errors="coerce").astype("Int64")

        df = df[df["Ano"] != 2022].copy()
        df = df[df["Mes_Num"].isin([5, 6, 7, 8])].copy()

        mapa_meses = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }

        df["Mes_Abrev"] = df["Mes_Num"].map(mapa_meses)
        df["AnoMes"] = df["Ano"].astype("Int64").astype(str) + "-" + df["Mes_Abrev"].fillna("")
        df.loc[df["Ano"].isna(), "AnoMes"] = None

    df_historico = df.copy()
    df_filtrado = df.copy()

    st.sidebar.subheader("🎯 Filtros")

    if "Ano" in df_filtrado.columns and df_filtrado["Ano"].notna().any():
        opcoes_ano = sorted(df_filtrado["Ano"].dropna().astype(int).unique().tolist())
        anos_sel = st.sidebar.multiselect(
            "Filtrar Ano(s)",
            options=opcoes_ano,
            default=opcoes_ano
        )

        if anos_sel:
            df_filtrado = df_filtrado[df_filtrado["Ano"].isin(anos_sel)]
        else:
            df_filtrado = df_filtrado.iloc[0:0]

    if coluna_comando:
        opcoes_comando = sorted(df_filtrado[coluna_comando].dropna().astype(str).unique())
        opcoes_comando = ["Todos"] + opcoes_comando
        comando_sel = st.sidebar.selectbox("Filtrar Comando", opcoes_comando, index=0)

        if comando_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado[coluna_comando].astype(str) == comando_sel]

    if coluna_cidade:
        opcoes_cidade = sorted(df_filtrado[coluna_cidade].dropna().astype(str).unique())
        opcoes_cidade = ["Todos"] + opcoes_cidade
        cidade_sel = st.sidebar.selectbox("Filtrar Cidade", opcoes_cidade, index=0)

        if cidade_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado[coluna_cidade].astype(str) == cidade_sel]

    if coluna_natureza:
        opcoes_natureza = sorted(df_filtrado[coluna_natureza].dropna().astype(str).unique())
        opcoes_natureza = ["Todos"] + opcoes_natureza
        natureza_sel = st.sidebar.selectbox("Filtrar Natureza", opcoes_natureza, index=0)

        if natureza_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado[coluna_natureza].astype(str) == natureza_sel]

    if coluna_data and df_filtrado[coluna_data].notna().any():
        data_min = df_filtrado[coluna_data].min().date()
        data_max = df_filtrado[coluna_data].max().date()

        intervalo = st.sidebar.date_input(
            "Filtrar Período",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )

        if isinstance(intervalo, tuple) and len(intervalo) == 2:
            data_ini, data_fim = intervalo
            df_filtrado = df_filtrado[
                (df_filtrado[coluna_data].dt.date >= data_ini) &
                (df_filtrado[coluna_data].dt.date <= data_fim)
            ]

    st.subheader("📚 Série Histórica Consolidada")
    st.caption("Os gráficos abaixo permanecem fixos e não são alterados pelos filtros operacionais da barra lateral.")

    if "Ano" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📊 Comparativo de Eventos por Ano")

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
            text_auto=True
        )

        fig.update_traces(
            marker_color=gerar_cores_alternadas(len(eventos_ano), PALETA_GRAFICO_1),
            textposition="outside",
            marker_line_color="rgba(255,255,255,0.45)",
            marker_line_width=0.8
        )

        fig = aplicar_layout_escuro(
            fig,
            xaxis_title="Ano",
            yaxis_title="Eventos",
            showlegend=False
        )
        fig.update_xaxes(type="category")

        st.plotly_chart(fig, use_container_width=True)

    if "Ano" in df_historico.columns and coluna_publico and df_historico["Ano"].notna().any():
        st.markdown("### 👥 Público Previsto por Ano")

        publico_ano = (
            df_historico.dropna(subset=["Ano"])
            .groupby("Ano")[coluna_publico]
            .sum()
            .reset_index()
            .sort_values("Ano")
        )

        publico_ano["Ano"] = publico_ano["Ano"].astype(int).astype(str)
        publico_ano["Publico_Label"] = publico_ano[coluna_publico].apply(formatar_milhares)

        fig = px.bar(
            publico_ano,
            x="Ano",
            y=coluna_publico,
            text="Publico_Label"
        )

        fig.update_traces(
            marker_color=gerar_cores_alternadas(len(publico_ano), PALETA_GRAFICO_2),
            textposition="outside",
            marker_line_color="rgba(255,255,255,0.45)",
            marker_line_width=0.8
        )

        fig = aplicar_layout_escuro(
            fig,
            xaxis_title="Ano",
            yaxis_title="Público Previsto",
            showlegend=False
        )
        fig.update_xaxes(type="category")

        st.plotly_chart(fig, use_container_width=True)

    if "Ano" in df_historico.columns and "Mes_Num" in df_historico.columns and df_historico["Ano"].notna().any():
        st.markdown("### 📅 Comparativo de Eventos por Mês e Ano")

        eventos_mes_ano = (
            df_historico.dropna(subset=["Ano", "Mes_Num"])
            .groupby(["Ano", "Mes_Num", "Mes_Abrev"])
            .size()
            .reset_index(name="Eventos")
            .sort_values(["Ano", "Mes_Num"])
        )

        eventos_mes_ano["Ano"] = eventos_mes_ano["Ano"].astype(int).astype(str)

        anos_ordenados = sorted(eventos_mes_ano["Ano"].dropna().unique())
        mapa_cores = {
            ano: PALETA_GRAFICO_3[i % len(PALETA_GRAFICO_3)]
            for i, ano in enumerate(anos_ordenados)
        }

        fig = px.bar(
            eventos_mes_ano,
            x="Mes_Abrev",
            y="Eventos",
            color="Ano",
            barmode="group",
            text_auto=True,
            color_discrete_map=mapa_cores
        )

        fig.update_traces(
            marker_line_color="rgba(255,255,255,0.45)",
            marker_line_width=0.8
        )

        fig = aplicar_layout_escuro(
            fig,
            xaxis_title="Mês",
            yaxis_title="Eventos",
            showlegend=True,
            legend_title="Ano"
        )

        st.plotly_chart(fig, use_container_width=True)

    if "AnoMes" in df_historico.columns and df_historico["AnoMes"].notna().any():
        st.markdown("### 📌 Eventos por Ano-Mês")

        ordem_meses = (
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
            categories=ordem_meses,
            ordered=True
        )
        eventos_anomes = eventos_anomes.sort_values("AnoMes")

        fig = px.bar(
            eventos_anomes,
            x="AnoMes",
            y="Eventos",
            text_auto=True
        )

        fig.update_traces(
            marker_color=gerar_cores_alternadas(len(eventos_anomes), PALETA_GRAFICO_4),
            textposition="outside",
            marker_line_color="rgba(255,255,255,0.45)",
            marker_line_width=0.8
        )

        fig = aplicar_layout_escuro(
            fig,
            xaxis_title="Ano-Mês",
            yaxis_title="Eventos",
            showlegend=False
        )
        fig.update_xaxes(type="category")

        st.plotly_chart(fig, use_container_width=True)

    if df_filtrado.empty:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")
        st.stop()

    st.subheader("📌 Indicadores Operacionais")

    total_eventos = len(df_filtrado)
    total_publico = int(df_filtrado[coluna_publico].sum()) if coluna_publico and coluna_publico in df_filtrado.columns and not df_filtrado.empty else 0
    total_cidades = df_filtrado[coluna_cidade].nunique() if coluna_cidade and coluna_cidade in df_filtrado.columns and not df_filtrado.empty else 0
    total_comandos = df_filtrado[coluna_comando].nunique() if coluna_comando and coluna_comando in df_filtrado.columns and not df_filtrado.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎉 Eventos", total_eventos)
    col2.metric("👥 Público Previsto", f"{total_publico:,}".replace(",", "."))
    col3.metric("🏙️ Cidades", total_cidades)
    col4.metric("🚔 Comandos", total_comandos)

    if coluna_natureza:
        st.subheader("🎭 Eventos por Natureza")

        natureza_eventos = (
            df_filtrado.dropna(subset=[coluna_natureza])
            .groupby(coluna_natureza)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )

        fig = px.pie(
            natureza_eventos,
            names=coluna_natureza,
            values="Eventos",
            hole=0.4
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    if coluna_tipo_publico:
        st.subheader("🥧 Tipo de Público")
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
            hole=0.4
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cobranca:
        st.subheader("🎟️ Tipo de Cobrança de Ingresso")

        cobranca_df = df_filtrado.copy()
        cobranca_df["Cobranca_Ajustada"] = cobranca_df[coluna_cobranca].apply(classificar_cobranca)

        pizza_cobranca = (
            cobranca_df.groupby("Cobranca_Ajustada")
            .size()
            .reset_index(name="Quantidade")
            .sort_values(by="Quantidade", ascending=False)
        )

        if not pizza_cobranca.empty:
            fig = px.pie(
                pizza_cobranca,
                names="Cobranca_Ajustada",
                values="Quantidade",
                hole=0.4,
                color="Cobranca_Ajustada",
                color_discrete_map={
                    "SIM": "#FF6B6B",
                    "NÃO": "#80ED99",
                    "NÃO INFORMADO": "#B0B0B0"
                }
            )
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados válidos para o gráfico de cobrança de ingresso.")

    if coluna_comando:
        st.subheader("🚔 Comandos com Mais Eventos")
        comando_eventos = (
            df_filtrado.groupby(coluna_comando)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
        )
        fig = px.bar(comando_eventos, x=coluna_comando, y="Eventos", color="Eventos", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade:
        st.subheader("🏙️ Cidades com Mais Eventos")
        cidade_eventos = (
            df_filtrado.groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(15)
        )
        fig = px.bar(cidade_eventos, x=coluna_cidade, y="Eventos", color="Eventos", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_evento and coluna_publico:
        st.subheader("🎯 Eventos com Maior Público Previsto")
        eventos_publico = (
            df_filtrado.groupby(coluna_evento)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(10)
        )
        fig = px.bar(eventos_publico, x=coluna_evento, y=coluna_publico, color=coluna_publico, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("📊 Distribuição do Público Previsto")
        fig = px.histogram(df_filtrado, x=coluna_publico, nbins=20)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_comando and coluna_publico:
        st.subheader("🚔 Público Previsto por Comando")
        publico_comando = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
        )
        fig = px.bar(publico_comando, x=coluna_comando, y=coluna_publico, color=coluna_publico, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade:
        st.subheader("🥧 Participação das Cidades")
        pizza_cidade = (
            df_filtrado.groupby(coluna_cidade)
            .size()
            .reset_index(name="Eventos")
            .sort_values(by="Eventos", ascending=False)
            .head(10)
        )
        fig = px.pie(pizza_cidade, names=coluna_cidade, values="Eventos", hole=0.4)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    if coluna_cidade and coluna_publico:
        st.subheader("📈 Média de Público por Cidade")
        media_cidade = (
            df_filtrado.groupby(coluna_cidade)[coluna_publico]
            .mean()
            .reset_index()
            .sort_values(by=coluna_publico, ascending=False)
            .head(15)
        )
        fig = px.line(media_cidade, x=coluna_cidade, y=coluna_publico, markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌡️ Intensidade de Público por Cidade")
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
                y=["Público"],
                colorscale="Reds"
            )
        )
        fig_heat.update_layout(
            height=450,
            template="plotly_dark",
            plot_bgcolor=FUNDO_PRETO,
            paper_bgcolor=FUNDO_PRETO,
            font=dict(color="white")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    if coluna_data and coluna_publico and df_filtrado[coluna_data].notna().any():
        st.subheader("📈 Evolução do Público")
        evolucao = (
            df_filtrado.dropna(subset=[coluna_data])
            .groupby(coluna_data)[coluna_publico]
            .sum()
            .reset_index()
            .sort_values(coluna_data)
        )
        fig = px.line(evolucao, x=coluna_data, y=coluna_publico, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    if coluna_publico:
        st.subheader("🔥 TOP 10 - Público Previsto")
        top_publico = df_filtrado.sort_values(by=coluna_publico, ascending=False).head(10)
        st.dataframe(top_publico, use_container_width=True)

    st.subheader("🧠 Análise Inteligente Operacional")

    if coluna_publico and not df_filtrado[coluna_publico].dropna().empty:
        maior_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmax()]
        menor_publico = df_filtrado.loc[df_filtrado[coluna_publico].idxmin()]
        media_geral = round(df_filtrado[coluna_publico].mean(), 2)
        mediana = round(df_filtrado[coluna_publico].median(), 2)

        nome_maior = maior_publico[coluna_evento] if coluna_evento else "N/D"
        nome_menor = menor_publico[coluna_evento] if coluna_evento else "N/D"

        st.info(f"""
🚨 Evento com MAIOR público previsto:
{nome_maior} ({int(maior_publico[coluna_publico]):,} pessoas)

⚠️ Evento com MENOR público previsto:
{nome_menor} ({int(menor_publico[coluna_publico]):,} pessoas)

📊 Média geral de público:
{media_geral:,.0f} pessoas

📈 Mediana de público:
{mediana:,.0f} pessoas

🎉 Total de eventos monitorados:
{len(df_filtrado)}

🏙️ Total de cidades:
{df_filtrado[coluna_cidade].nunique() if coluna_cidade else 0}

🚔 Total de comandos:
{df_filtrado[coluna_comando].nunique() if coluna_comando else 0}
""")

    if coluna_comando and coluna_publico:
        st.subheader("🏆 Ranking Operacional dos Comandos")
        ranking_operacional = (
            df_filtrado.groupby(coluna_comando)[coluna_publico]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )
        ranking_operacional.columns = ["Comando", "Público Total", "Média Público", "Eventos"]
        st.dataframe(ranking_operacional, use_container_width=True)

    st.subheader("📄 Dados Operacionais")
    pesquisa_final = st.text_input("🔎 Pesquisar na tabela final", key="pesquisa_final")

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
        label="⬇️ Baixar CSV",
        data=csv,
        file_name="festas_juninas_filtrado.csv",
        mime="text/csv"
    )

    st.success(f"✅ Dashboard atualizado automaticamente em {horario}")

except Exception as erro:
    st.error(f"Erro ao carregar dados: {erro}")