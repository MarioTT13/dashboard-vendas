import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página para um visual mais profissional
st.set_page_config(page_title="Gestão Estratégica 360", layout="wide", initial_sidebar_state="expanded")

# CSS para customizar as métricas e deixar mais chamativo
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Dashboard de Gestão Estratégica")
st.markdown("---")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data # Cache para carregar rápido
def load_data(file):
    if file is not None:
        return pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
    try:
        return pd.read_excel("vendas.xlsx")
    except:
        return None

file = st.sidebar.file_uploader("📂 Atualizar Base de Dados", type=["xlsx", "csv"])
df = load_data(file)

if df is not None:
    # Padronização de colunas (Lógica Detetive)
    cols = df.columns.tolist()
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'venda', 'total'])), None)
    col_custo = next((c for c in cols if any(kw in c.lower() for kw in ['custo'])), None)
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia'])), None)
    col_prod = next((c for c in cols if any(kw in c.lower() for kw in ['produto', 'item', 'desc'])), cols[0])
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat'])), col_prod)

    if col_data:
        df[col_data] = pd.to_datetime(df[col_data])

    # --- FILTROS LATERAIS ---
    st.sidebar.subheader("🔍 Filtros de Decisão")
    
    if col_data:
        min_d, max_d = df[col_data].min().date(), df[col_data].max().date()
        periodo = st.sidebar.date_input("Período de Análise", [min_d, max_d])
        if len(periodo) == 2:
            df = df[(df[col_data].dt.date >= periodo[0]) & (df[col_data].dt.date <= periodo[1])]

    categorias = st.sidebar.multiselect("Filtrar Categorias", df[col_cat].unique(), default=df[col_cat].unique())
    df = df[df[col_cat].isin(categorias)]

    # --- CÁLCULOS ESTRATÉGICOS ---
    faturamento = df[col_valor].sum()
    qtd_vendas = len(df)
    ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else 0
    
    # Cálculo de Lucro (se houver coluna de custo)
    if col_custo:
        lucro_total = (df[col_valor] - df[col_custo]).sum()
        margem = (lucro_total / faturamento) * 100 if faturamento > 0 else 0
    else:
        lucro_total = faturamento * 0.3 # Estimativa de 30% se não houver custo
        margem = 30.0

    # --- KPIs (INDICADORES CHAVE) ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Faturamento", f"R$ {faturamento:,.2f}")
    kpi2.metric("📈 Lucro Estimado", f"R$ {lucro_total:,.2f}")
    kpi3.metric("🛒 Ticket Médio", f"R$ {ticket_medio:,.2f}")
    kpi4.metric("📊 Margem", f"{margem:.1f}%")

    st.markdown("---")

    # --- GRÁFICOS ---
    col_graf1, col_graf2 = st.columns([6, 4])

    with col_graf1:
        st.subheader("📅 Desempenho de Vendas no Tempo")
        if col_data:
            df_tempo = df.groupby(col_data)[col_valor].sum().reset_index()
            fig_lin = px.area(df_tempo, x=col_data, y=col_valor, title="Faturamento Diário", line_shape='spline')
            st.plotly_chart(fig_lin, use_container_width=True)

    with col_graf2:
        st.subheader("🏆 Top Produtos/Categorias")
        top_df = df.groupby(col_cat)[col_valor].sum().sort_values(ascending=False).reset_index()
        fig_bar = px.bar(top_df, x=col_valor, y=col_cat, orientation='h', color=col_valor, color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ANÁLISE DE PRODUTOS ---
    st.subheader("🧐 Análise Detalhada de Itens")
    st.dataframe(df[[col_prod, col_cat, col_valor]].sort_values(by=col_valor, ascending=False), use_container_width=True)

else:
    st.warning("Aguardando base de dados para análise...")
