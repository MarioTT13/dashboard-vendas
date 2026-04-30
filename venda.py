import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA PARA CELULAR ---
st.set_page_config(page_title="Dashboard BI Elite", layout="wide")

# Exemplo de dados com Preço de Compra e Venda
data = {
    'Produto': ['Anel Elástico', 'Eixo A', 'Eixo B', 'Retentor X', 'Gaxeta Y'],
    'Categoria': ['Fixação', 'Eixos', 'Eixos', 'Vedação', 'Vedação'],
    'Qtd_Vendida': [150, 80, 45, 120, 30],
    'Preco_Compra': [1.50, 45.00, 55.00, 12.00, 25.00],
    'Preco_Venda': [3.50, 85.00, 95.00, 28.00, 58.00],
    'Data': pd.date_range(start='2024-01-01', periods=5, freq='D')
}
df = pd.DataFrame(data)

# Cálculos de Margem
df['Faturamento'] = df['Qtd_Vendida'] * df['Preco_Venda']
df['Lucro_Total'] = (df['Preco_Venda'] - df['Preco_Compra']) * df['Qtd_Vendida']

st.title("🚀 Inteligência Comercial")

# --- BLOCO 1: MÉTRICAS (Fica ótimo no celular) ---
m1, m2 = st.columns(2)
with m1:
    st.metric("Faturamento Total", f"R$ {df['Faturamento'].sum():,.2f}")
with m2:
    st.metric("Lucro Estimado", f"R$ {df['Lucro_Total'].sum():,.2f}", delta="15%")

st.markdown("---")

# --- BLOCO 2: O GRÁFICO DE VELAS (ESTILO TRADING) ---
st.subheader("📊 Tendência de Valorização (Velas)")
# Simulando dados de OHLC (Abertura, Máximo, Mínimo, Fechamento) para o visual
fig_velas = go.Figure(data=[go.Candlestick(
    x=df['Data'],
    open=df['Preco_Venda'] * 0.9,
    high=df['Preco_Venda'] * 1.1,
    low=df['Preco_Venda'] * 0.8,
    close=df['Preco_Venda'],
    increasing_line_color= '#00cc96', decreasing_line_color= '#ff3e3e'
)])
fig_velas.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig_velas, use_container_width=True)

# --- BLOCO 3: RANKING DE PRODUTOS (O QUE MAIS SAI VS MENOS SAI) ---
st.subheader("🏆 Ranking de Performance")
tab1, tab2 = st.tabs(["🔝 Top Saída", "📉 Menos Saída"])

with tab1:
    top_vendas = df.nlargest(5, 'Qtd_Vendida')[['Produto', 'Qtd_Vendida', 'Preco_Venda']]
    st.table(top_vendas)

with tab2:
    bottom_vendas = df.nsmallest(5, 'Qtd_Vendida')[['Produto', 'Qtd_Vendida', 'Preco_Venda']]
    st.table(bottom_vendas)

# --- BLOCO 4: DETALHAMENTO DE PREÇOS E MARGEM ---
st.subheader("💰 Análise de Margem por Item")
# Criando um gráfico de barras horizontais para ver o lucro por produto
fig_margem = px.bar(
    df, 
    x='Lucro_Total', 
    y='Produto', 
    orientation='h',
    text_auto='.2s',
    color='Lucro_Total',
    color_continuous_scale='Blues'
)
fig_margem.update_layout(template="plotly_dark", height=300)
st.plotly_chart(fig_margem, use_container_width=True)
