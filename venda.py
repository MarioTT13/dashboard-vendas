import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="BI & Automação Comercial")

# 2. Dados Fictícios Detalhados (Simulando sua base de dados)
data = {
    'Produto': ['Anel Elástico', 'Eixo A', 'Eixo B', 'Retentor X', 'Gaxeta Y', 'Anel O-Ring', 'Parafuso Inox'],
    'Categoria': ['Fixação', 'Eixos', 'Eixos', 'Vedação', 'Vedação', 'Vedação', 'Fixação'],
    'Qtd_Vendida': [150, 80, 45, 120, 30, 200, 500],
    'Preco_Compra': [1.50, 45.00, 55.00, 12.00, 25.00, 0.50, 0.20],
    'Preco_Venda': [3.50, 85.00, 95.00, 28.00, 58.00, 1.20, 0.45],
    'Data': pd.to_datetime(['2024-04-01', '2024-04-05', '2024-04-10', '2024-04-15', '2024-04-20', '2024-04-25', '2024-04-28'])
}
df = pd.DataFrame(data)

# Cálculos Base
df['Faturamento'] = df['Qtd_Vendida'] * df['Preco_Venda']
df['Lucro'] = (df['Preco_Venda'] - df['Preco_Compra']) * df['Qtd_Vendida']

# --- 3. BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros Estratégicos")

# Filtro de Categoria
categorias = st.sidebar.multiselect(
    "Selecione a Categoria:",
    options=df['Categoria'].unique(),
    default=df['Categoria'].unique()
)

# Filtro de Data
data_inicial = st.sidebar.date_input("Início:", df['Data'].min())
data_final = st.sidebar.date_input("Fim:", df['Data'].max())

# Aplicando os filtros ao DataFrame
df_filtrado = df[
    (df['Categoria'].isin(categorias)) & 
    (df['Data'] >= pd.to_datetime(data_inicial)) & 
    (df['Data'] <= pd.to_datetime(data_final))
]

# --- 4. LAYOUT PRINCIPAL ---
st.title("🚀 Painel de Inteligência Comercial")

# Métricas Principais
c1, c2, c3 = st.columns(3)
c1.metric("Faturamento Filtrado", f"R$ {df_filtrado['Faturamento'].sum():,.2f}")
c2.metric("Lucro Estimado", f"R$ {df_filtrado['Lucro'].sum():,.2f}")
c3.metric("Ticket Médio (Qtd)", f"{df_filtrado['Qtd_Vendida'].mean():,.0f} un")

st.markdown("---")

# 5. Gráfico de Velas (Candlestick) - Evolução de Preços
st.subheader("📈 Evolução e Volatilidade de Preços")
fig_velas = go.Figure(data=[go.Candlestick(
    x=df_filtrado['Data'],
    open=df_filtrado['Preco_Venda'] * 0.98,
    high=df_filtrado['Preco_Venda'] * 1.05,
    low=df_filtrado['Preco_Venda'] * 0.92,
    close=df_filtrado['Preco_Venda'],
    increasing_line_color='#00d1ff', decreasing_line_color='#ff3e3e'
)])
fig_velas.update_layout(xaxis_rangeslider_visible=False, height=350, template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig_velas, use_container_width=True)

# 6. Rankings e Mix (Lado a lado no PC, empilhado no Celular)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🏆 O que mais sai (Top Qtd)")
    st.dataframe(
        df_filtrado.nlargest(5, 'Qtd_Vendida')[['Produto', 'Qtd_Vendida', 'Preco_Compra', 'Preco_Venda']],
        use_container_width=True, hide_index=True
    )
    
    st.subheader("📉 Menos Saída")
    st.dataframe(
        df_filtrado.nsmallest(5, 'Qtd_Vendida')[['Produto', 'Qtd_Vendida', 'Preco_Compra', 'Preco_Venda']],
        use_container_width=True, hide_index=True
    )

with col2:
    st.subheader("🎯 Mix por Faturamento")
    fig_rosca = px.pie(df_filtrado, values='Faturamento', names='Categoria', hole=0.6)
    fig_rosca.update_traces(textposition='outside', textinfo='label+percent')
    fig_rosca.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_rosca, use_container_width=True)
