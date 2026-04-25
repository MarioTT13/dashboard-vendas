import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inteligente", layout="wide")

st.title("📊 Painel de Inteligência Adaptável")

# --- BARRA LATERAL ---
st.sidebar.header("📥 Entrada de Dados")
uploaded_file = st.sidebar.file_uploader("Suba sua planilha (Excel ou CSV)", type=["xlsx", "csv"])

def carregar_dados():
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    try:
        return pd.read_excel("vendas.xlsx")
    except:
        return None

df = carregar_dados()

if df is not None:
    cols = df.columns.tolist()
    
    # Identificação Automática
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'preço', 'preco', 'total', 'faturamento', 'venda'])), cols[-1])
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat', 'nome', 'produto', 'item', 'descrição', 'desc'])), cols[0])
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia', 'mês', 'mes', 'emissão'])), None)

    # --- CONFIGURAÇÃO DOS FILTROS NA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtros de Visualização")

    # 1. Filtro de Data (se existir coluna de data)
    df_filtrado = df.copy()
    if col_data:
        df[col_data] = pd.to_datetime(df[col_data])
        min_date = df[col_data].min().date()
        max_date = df[col_data].max().date()
        
        intervalo_data = st.sidebar.date_input(
            "Selecione o Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Aplicar filtro de data apenas se o intervalo estiver completo
        if len(intervalo_data) == 2:
            start_date, end_date = intervalo_data
            df_filtrado = df[(df[col_data].dt.date >= start_date) & (df[col_data].dt.date <= end_date)]

    # 2. Filtro de Categoria
    lista_categorias = df_filtrado[col_cat].unique().tolist()
    categorias_selecionadas = st.sidebar.multiselect(f"Filtrar {col_cat}", lista_categorias, default=lista_categorias)
    df_filtrado = df_filtrado[df_filtrado[col_cat].isin(categorias_selecionadas)]

    # --- MÉTRICAS ---
    total = df_filtrado[col_valor].sum()
    qtd = len(df_filtrado)
    ticket = total / qtd if qtd > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento no Período", f"R$ {total:,.2f}")
    m2.metric("Vendas Realizadas", qtd)
    m3.metric("Ticket Médio", f"R$ {ticket:,.2f}")

    st.markdown("---")

    # --- GRÁFICOS ---
    c_esq, c_dir = st.columns(2)

    with c_esq:
        st.subheader(f"Peso por {col_cat}")
        fig_rosca = px.pie(df_filtrado, values=col_valor, names=col_cat, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_rosca, use_container_width=True)

    with c_dir:
        if col_data:
            st.subheader("Evolução Diária")
            df_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index()
            fig_linha = px.line(df_tempo, x=col_data, y=col_valor, markers=True, line_shape="spline")
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("Adicione uma coluna de data para ver a evolução temporal.")

    # Tabela final
    st.subheader("📋 Detalhamento")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.info("Suba uma planilha para começar a análise.")
