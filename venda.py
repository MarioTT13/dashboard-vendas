import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão Estratégica 360", layout="wide")

# Estilo para métricas e fundo
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 26px; color: #007bff; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Inteligência Comercial")

# --- CARREGAMENTO ---
def load_data(file):
    if file is not None:
        return pd.read_excel(file) if any(file.name.endswith(ext) for ext in ['xlsx', 'xls', 'xlns']) else pd.read_csv(file)
    for nome in ["vendas.xlsx", "vendas.xlns"]:
        try: return pd.read_excel(nome)
        except: continue
    return None

file = st.sidebar.file_uploader("📂 Atualizar Base", type=["xlsx", "csv", "xlns"])
df = load_data(file)

if df is not None:
    cols = df.columns.tolist()
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'venda', 'total'])), None)
    col_custo = next((c for c in cols if any(kw in c.lower() for kw in ['custo'])), None)
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia'])), None)
    col_prod = next((c for c in cols if any(kw in c.lower() for kw in ['produto', 'item'])), cols[0])
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat'])), col_prod)
    col_qtd = next((c for c in cols if any(kw in c.lower() for kw in ['qtd', 'quantidade'])), None)

    # --- FILTROS ---
    st.sidebar.header("⚙️ Filtros")
    
    # Filtro de Categoria
    lista_cats = df[col_cat].unique().tolist()
    sel_cats = st.sidebar.multiselect("Categorias", lista_cats, default=lista_cats)
    df_filtrado = df[df[col_cat].isin(sel_cats)].copy()

    # Filtro de Data
    if col_data:
        df_filtrado[col_data] = pd.to_datetime(df_filtrado[col_data])
        min_d, max_d = df_filtrado[col_data].min().date(), df_filtrado[col_data].max().date()
        periodo = st.sidebar.date_input("Período", [min_d, max_d])
        if len(periodo) == 2:
            df_filtrado = df_filtrado[(df_filtrado[col_data].dt.date >= periodo[0]) & (df_filtrado[col_data].dt.date <= periodo[1])]

    # --- CÁLCULOS ---
    faturamento = df_filtrado[col_valor].sum()
    lucro = (df_filtrado[col_valor] - df_filtrado[col_custo]).sum() if col_custo else faturamento * 0.3
    margem = (lucro / faturamento * 100) if faturamento > 0 else 0
    
    # Ticket Médio
    qtd_total = df_filtrado[col_qtd].sum() if col_qtd else len(df_filtrado)
    ticket_medio = faturamento / qtd_total if qtd_total > 0 else 0

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Faturamento", f"R$ {faturamento:,.2f}")
    m2.metric("📈 Lucro", f"R$ {lucro:,.2f}")
    m3.metric("🎯 Margem", f"{margem:.1f}%")
    m4.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")

    # --- GRÁFICO DE BARRAS (O que você preferiu) ---
    if col_data:
        st.subheader("📊 Evolução de Vendas por Período")
        df_tempo = df_filtrado.groupby(col_data)[col_valor].sum().reset_index()
        
        fig_barras = px.bar(
            df_tempo, x=col_data, y=col_valor,
            color=col_valor, # Barra muda de cor conforme o valor (Efeito visual top)
            color_continuous_scale='Blues',
            text_auto='.2s'
        )
        
        fig_barras.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=None, yaxis_title=None,
            coloraxis_showscale=False,
            height=400,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    # --- MIX E RANKING ---
    st.markdown("---")
    c_l, c_r = st.columns([1, 1])

    with c_l:
        st.subheader("🎯 Mix por Categoria")
        fig_rosca = px.pie(df_filtrado, values=col_valor, names=col_cat, hole=0.6)
        fig_rosca.update_traces(
            textinfo='percent', 
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>"
        )
        fig_rosca.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_rosca, use_container_width=True)

    with c_r:
        st.subheader("🏆 Melhores Itens")
        top_itens = df_filtrado.groupby(col_prod)[col_valor].sum().nlargest(5).reset_index()
        st.dataframe(top_itens, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📄 Base de Dados")
    st.dataframe(df_filtrado, use_container_width=True)
