import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Universal", layout="wide")

st.title("📊 Painel de Inteligência Adaptável")
st.info("Este painel se ajusta automaticamente às colunas da sua planilha.")

# --- BARRA LATERAL ---
st.sidebar.header("📥 Entrada de Dados")
uploaded_file = st.sidebar.file_uploader("Suba qualquer planilha de vendas", type=["xlsx", "csv"])

def carregar_dados():
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    try:
        return pd.read_excel("vendas.xlsx")
    except:
        return None

df = carregar_dados()

if df is not None:
    # --- LÓGICA DE IDENTIFICAÇÃO AUTOMÁTICA ---
    cols = df.columns.tolist()
    
    # Tenta achar a coluna de VALOR (procurando por nomes comuns)
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'preço', 'preco', 'total', 'faturamento', 'venda'])), cols[-1])
    
    # Tenta achar a coluna de CATEGORIA/NOME
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat', 'nome', 'produto', 'item', 'descrição', 'desc'])), cols[0])

    # Tenta achar a coluna de DATA
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia', 'mês', 'mes', 'emissão'])), None)

    if col_data:
        df[col_data] = pd.to_datetime(df[col_data])

    # --- FILTROS DINÂMICOS NA LATERAL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtros")
    
    # Filtro de Categoria (pega os valores únicos da coluna identificada)
    lista_categorias = df[col_cat].unique().tolist()
    categorias_selecionadas = st.sidebar.multiselect("Filtrar por " + col_cat, lista_categorias, default=lista_categorias)

    # Aplicando o filtro
    df_filtrado = df[df[col_cat].isin(categorias_selecionadas)]

    # --- EXIBIÇÃO DE MÉTRICAS ---
    total = df_filtrado[col_valor].sum()
    qtd = len(df_filtrado)
    
    c1, c2 = st.columns(2)
    c1.metric(f"Total em {col_valor}", f"R$ {total:,.2f}")
    c2.metric("Quantidade de Registros", qtd)

    # --- GRÁFICOS DINÂMICOS ---
    st.markdown("---")
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("Divisão por " + col_cat)
        fig_rosca = px.pie(df_filtrado, values=col_valor, names=col_cat, hole=0.4)
        st.plotly_chart(fig_rosca, use_container_width=True)

    with col_dir:
        st.subheader("Evolução Financeira")
        if col_data:
            df_venda_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index()
            fig_linha = px.line(df_venda_tempo, x=col_data, y=col_valor, markers=True)
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.warning("Coluna de data não encontrada para gerar gráfico de linha.")

    st.subheader("📋 Visualização dos Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.warning("Aguardando planilha...")
