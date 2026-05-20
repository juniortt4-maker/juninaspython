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

# URL CORRIGIDA DA PLANILHA GOOGLE SHEETS
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

    st.success(f"✅ DASHBOARD ATUALIZADO EM {horario}")

except Exception as erro:
    st.error(f"ERRO AO CARREGAR DADOS: {str(erro).upper()}")
