import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Painel de Lucro Real", layout="wide")

st.title("📊 Painel de Inteligência de Negócio")
st.markdown("---")

# Menu lateral para upload ou status
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Suba sua planilha de vendas", type=["xlsx"])

# Lógica para carregar os dados
df = None

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    # Tenta carregar automaticamente se o arquivo estiver na pasta
    try:
        df = pd.read_excel("vendas.xlsx")
        st.sidebar.success("Planilha 'vendas.xlsx' carregada automaticamente!")
    except:
        st.sidebar.info("Aguardando upload da planilha ou arquivo 'vendas.xlsx' na pasta.")

# Se os dados foram carregados, mostra o dashboard
if df is not None:
    # Cálculos das métricas
    total_vendas = df['Valor'].sum()
    quantidade = len(df)
    # Cálculo de lucro fictício (ex: 30%) - você pode ajustar isso depois
    lucro_estimado = total_vendas * 0.30 

    # Exibição das métricas em colunas
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")
    col2.metric("Nº de Vendas", quantidade)
    col3.metric("Lucro Estimado (30%)", f"R$ {lucro_estimado:,.2f}")

    st.markdown("---")

    # Gráfico de Barras
    st.subheader("📈 Vendas por Categoria")
    vendas_por_cat = df.groupby('Categoria')['Valor'].sum().reset_index()
    fig = px.bar(vendas_por_cat, x='Categoria', y='Valor', 
                 color='Categoria', 
                 text_auto='.2s',
                 title="Distribuição de Receita")
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de Dados
    with st.expander("Ver dados brutos"):
        st.write(df)
else:
    # Tela amigável caso não tenha dados ainda
    st.warning("⚠️ Nenhuma informação encontrada.")
    st.info("Dica: Verifique se o arquivo que você baixou está com o nome correto (vendas.xlsx) na mesma pasta deste código ou use o menu lateral para subir o arquivo.")