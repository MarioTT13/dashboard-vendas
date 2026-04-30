import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gestão Estratégica 360", layout="wide")

# Estilo para métricas e fundo (Mantendo seu estilo original)
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
    col_qtd = next((c for c in cols if any(kw in c.lower() for kw in ['qtd', 'quantidade'])), None)

    df_filtrado = df.copy()

    if col_data:
        df_filtrado[col_data] = pd.to_datetime(df_filtrado[col_data])
        min_d, max_d = df_filtrado[col_data].min().date(), df_filtrado[col_data].max().date()
        periodo = st.sidebar.date_input("Período de Análise", [min_d, max_d])
        if len(periodo) == 2:
            df_filtrado = df_filtrado[(df_filtrado[col_data].dt.date >= periodo[0]) & (df_filtrado[col_data].dt.date <= periodo[1])]

    # --- MÉTRICAS (Incluindo Ticket Médio que você pediu agora) ---
    faturamento = df_filtrado[col_valor].sum()
    lucro = (df_filtrado[col_valor] - df_filtrado[col_custo]).sum() if col_custo else faturamento * 0.3
    margem = (lucro / faturamento) * 100 if faturamento > 0 else 0
    
    qtd_total = df_filtrado[col_qtd].sum() if col_qtd else len(df_filtrado)
    ticket_medio = faturamento / qtd_total if qtd_total > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Faturamento Total", f"R$ {faturamento:,.2f}")
    m2.metric("📈 Lucro Estimado", f"R$ {lucro:,.2f}")
    m3.metric("📊 Margem", f"{margem:.1f}%")
    m4.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")

    # --- GRÁFICO PRINCIPAL: AGORA EM BARRAS ---
    if col_data:
        st.subheader("📊 Inteligência de Mercado e Evolução")
        df_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index().sort_values(by=col_data)
        
        fig_barras = px.bar(
            df_tempo, 
            x=col_data, 
            y=col_valor,
            text_auto='.2s',
            color_discrete_sequence=['#00D1FF'] # O azul neon que você gosta
        )

        fig_barras.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.1)', tickprefix="R$ "),
            margin=dict(l=0, r=0, t=20, b=0),
            height=450
        )

        st.plotly_chart(fig_barras, use_container_width=True)

    # --- ÁREA INFERIOR: SEU GRÁFICO DE ROSCA ORIGINAL ---
    st.markdown("---")
    col_inf1, col_inf2 = st.columns([4, 6])
    
    with col_inf1:
        st.subheader("🎯 Mix de Categorias")
        fig_rosca = px.pie(
            df_filtrado, 
            values=col_valor, 
            names=col_cat, 
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        # Limpeza do Hover como você pediu
        fig_rosca.update_traces(
            textposition='outside', 
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<extra></extra>"
        )
        fig_rosca.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0), height=400)
        st.plotly_chart(fig_rosca, use_container_width=True)

    with col_inf2:
        st.subheader("🏆 Performance de Itens")
        tab1, tab2 = st.tabs(["🔝 Mais Vendidos", "📉 Menos Vendidos"])
        with tab1:
            st.dataframe(df_filtrado.groupby(col_prod)[col_valor].sum().nlargest(5).reset_index(), use_container_width=True, hide_index=True)
        with tab2:
            st.dataframe(df_filtrado.groupby(col_prod)[col_valor].sum().nsmallest(5).reset_index(), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📄 Base de Dados")
    st.dataframe(df_filtrado, use_container_width=True)
