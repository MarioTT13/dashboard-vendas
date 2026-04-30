import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gestão Estratégica 360", layout="wide")

# Estilo para métricas e fundo
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Dashboard de Gestão Estratégica")

# --- CARREGAMENTO ROBUSTO (SEU CÓDIGO) ---
def load_data(file):
    if file is not None:
        return pd.read_excel(file) if any(file.name.endswith(ext) for ext in ['xlsx', 'xls', 'xlns']) else pd.read_csv(file)
    for nome in ["vendas.xlsx", "vendas.xlns"]:
        try: return pd.read_excel(nome)
        except: continue
    return None

file = st.sidebar.file_uploader("📂 Atualizar Base de Dados", type=["xlsx", "csv", "xlns"])
df = load_data(file)

if df is not None:
    cols = df.columns.tolist()
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'venda', 'total'])), None)
    col_custo = next((c for c in cols if any(kw in c.lower() for kw in ['custo'])), None)
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia'])), None)
    col_prod = next((c for c in cols if any(kw in c.lower() for kw in ['produto', 'item'])), cols[0])
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat'])), col_prod)

    df_filtrado = df.copy()

    if col_data:
        df_filtrado[col_data] = pd.to_datetime(df_filtrado[col_data])
        min_d, max_d = df_filtrado[col_data].min().date(), df_filtrado[col_data].max().date()
        periodo = st.sidebar.date_input("Período de Análise", [min_d, max_d])
        if len(periodo) == 2:
            df_filtrado = df_filtrado[(df_filtrado[col_data].dt.date >= periodo[0]) & (df_filtrado[col_data].dt.date <= periodo[1])]

    # --- MÉTRICAS ---
    faturamento = df_filtrado[col_valor].sum()
    lucro = (df_filtrado[col_valor] - df_filtrado[col_custo]).sum() if col_custo else faturamento * 0.3
    margem = (lucro / faturamento) * 100 if faturamento > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Faturamento Total", f"R$ {faturamento:,.2f}")
    m2.metric("📈 Lucro Estimado", f"R$ {lucro:,.2f}")
    m3.metric("📊 Margem", f"{margem:.1f}%")

    st.markdown("---")

    # --- NOVO: GRÁFICO DE VELAS (Substituindo a linha simples) ---
    if col_data:
        st.subheader("📈 Inteligência de Mercado e Evolução (Velas)")
        
        df_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index().sort_values(by=col_data)
        
        # Criando o gráfico de Velas simulado pela variação do faturamento diário
        fig_velas = go.Figure(data=[go.Candlestick(
            x=df_tempo[col_data],
            open=df_tempo[col_valor] * 0.9,
            high=df_tempo[col_valor] * 1.1,
            low=df_tempo[col_valor] * 0.8,
            close=df_tempo[col_valor],
            increasing_line_color='#00D1FF', # Seu Azul Neon
            decreasing_line_color='#FF3E3E'  # Vermelho para queda
        )])

        fig_velas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            height=400,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_velas, use_container_width=True)

    # --- SEÇÃO DE MIX (SUA ROSCA ORIGINAL) ---
    st.markdown("---")
    col_inf1, col_inf2 = st.columns([4, 6])
    
    with col_inf1:
        st.subheader("🎯 Mix por Categoria")
        fig_rosca = px.pie(df_filtrado, values=col_valor, names=col_cat, hole=0.6,
                           color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_rosca.update_traces(textposition='outside', textinfo='label+percent')
        fig_rosca.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_rosca, use_container_width=True)

    # --- NOVO: RANKING DE PRODUTOS (TOP VS BOTTOM) ---
    with col_inf2:
        st.subheader("🏆 Performance de Produtos")
        tab1, tab2 = st.tabs(["🔝 Mais Vendidos", "📉 Menos Vendidos"])
        
        with tab1:
            top_prod = df_filtrado.groupby(col_prod)[col_valor].sum().nlargest(5).reset_index()
            st.dataframe(top_prod, use_container_width=True, hide_index=True)
            
        with tab2:
            bottom_prod = df_filtrado.groupby(col_prod)[col_valor].sum().nsmallest(5).reset_index()
            st.dataframe(bottom_prod, use_container_width=True, hide_index=True)

    # --- BASE DE DADOS (SUA PLANILHA NO FINAL) ---
    st.markdown("---")
    st.subheader("📄 Base de Dados Completa")
    st.dataframe(df_filtrado, use_container_width=True)
