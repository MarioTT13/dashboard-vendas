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

  # --- ÁREA DE GRÁFICOS ESTILIZADOS ---
    st.markdown("---")
    if col_data:
        st.subheader("📈 Inteligência de Mercado e Evolução")
        
        # Agrupamento e Ordenação
        df_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index().sort_values(by=col_data)
        
        import plotly.graph_objects as go

        # Criando o gráfico com preenchimento em gradiente
        fig_evolucao = go.Figure()

        fig_evolucao.add_trace(go.Scatter(
            x=df_tempo[col_data], 
            y=df_tempo[col_valor],
            mode='lines+markers',
            line=dict(width=4, color='#00D1FF', shape='spline'), # Linha Neon Suave
            fill='tozeroy', # Preenchimento até o eixo zero
            fillcolor='rgba(0, 209, 255, 0.15)', # Azul transparente
            marker=dict(size=8, color='white', line=dict(width=2, color='#00D1FF')),
            name='Faturamento'
        ))

        # Ajustes de Layout para "Vibe" Tech
        fig_evolucao.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(200,200,200,0.1)', 
                zeroline=False,
                tickprefix="R$ "
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            height=450
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

    # Gráfico de Categorias (Rosca Moderna)
    st.markdown("---")
    col_inf1, col_inf2 = st.columns([4, 6])
    
    with col_inf1:
        st.subheader("🎯 Mix de Produtos")
        fig_rosca = px.pie(
            df_filtrado, 
            values=col_valor, 
            names=col_cat, 
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
        fig_rosca.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_rosca, use_container_width=True)

    with col_inf2:
        st.subheader("📋 Visão Consolidada")
        st.dataframe(df_filtrado[[col_prod, col_valor]].sort_values(by=col_valor, ascending=False), use_container_width=True)

    # --- ANÁLISE DE PRODUTOS ---
    st.subheader("🧐 Análise Detalhada de Itens")
    st.dataframe(df[[col_prod, col_cat, col_valor]].sort_values(by=col_valor, ascending=False), use_container_width=True)

else:
    st.warning("Aguardando base de dados para análise...")
