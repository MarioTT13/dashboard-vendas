import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gestão Estratégica 360", layout="wide")

# Estilo para métricas e fundo (Visual Premium Dark)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 26px; color: #00D1FF; font-weight: bold; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Inteligência Comercial Pro")

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
    # Identificação de colunas (Seu código original robusto)
    cols = df.columns.tolist()
    col_valor = next((c for c in cols if any(kw in c.lower() for kw in ['valor', 'venda', 'total'])), None)
    col_custo = next((c for c in cols if any(kw in c.lower() for kw in ['custo'])), None)
    col_data = next((c for c in cols if any(kw in c.lower() for kw in ['data', 'dia'])), None)
    col_prod = next((c for c in cols if any(kw in c.lower() for kw in ['produto', 'item'])), cols[0])
    col_cat = next((c for c in cols if any(kw in c.lower() for kw in ['cat'])), col_prod)
    col_qtd = next((c for c in cols if any(kw in c.lower() for kw in ['qtd', 'quantidade', 'unidades'])), None)

    # --- FILTROS ---
    st.sidebar.markdown("### ⚙️ Filtros")
    lista_categorias = df[col_cat].unique().tolist()
    categorias_selecionadas = st.sidebar.multiselect("Categorias", lista_categorias, default=lista_categorias)
    
    df_filtrado = df[df[col_cat].isin(categorias_selecionadas)].copy()

    if col_data:
        df_filtrado[col_data] = pd.to_datetime(df_filtrado[col_data])
        min_d, max_d = df_filtrado[col_data].min().date(), df_filtrado[col_data].max().date()
        periodo = st.sidebar.date_input("Período", [min_d, max_d])
        if len(periodo) == 2:
            df_filtrado = df_filtrado[(df_filtrado[col_data].dt.date >= periodo[0]) & (df_filtrado[col_data].dt.date <= periodo[1])]

   # --- CÁLCULOS DAS MÉTRICAS (CORRIGIDO) ---
# Criamos o Faturamento Total por linha primeiro (Preço x Qtd)
if col_qtd:
    df_filtrado['Faturamento_Real'] = df_filtrado[col_valor] * df_filtrado[col_qtd]
else:
    df_filtrado['Faturamento_Real'] = df_filtrado[col_valor]

# Agora usamos o Faturamento_Real para todas as contas
faturamento = df_filtrado['Faturamento_Real'].sum()

# Cálculo do Lucro (Usando o faturamento real)
if col_custo:
    # Se tiver custo, lucro é (Preço Total - Custo Total)
    # Importante: Verifique se o seu custo também precisa ser multiplicado pela Qtd!
    total_custo = (df_filtrado[col_custo] * df_filtrado[col_qtd]).sum() if col_qtd else df_filtrado[col_custo].sum()
    lucro = faturamento - total_custo
else:
    lucro = faturamento * 0.3

    margem = (lucro / faturamento * 100) if faturamento > 0 else 0

# Cálculo do Ticket Médio
 qtd_total = df_filtrado[col_qtd].sum() if col_qtd else len(df_filtrado)
 ticket_medio = faturamento / qtd_total if qtd_total > 0 else 0
    
 # --- EXIBIÇÃO DAS MÉTRICAS (4 Colunas) ---
     m1, m2, m3, m4 = st.columns(4)
     m1.metric("💰 Faturamento", f"R$ {faturamento:,.2f}")
     m2.metric("📈 Lucro Real", f"R$ {lucro:,.2f}")
     m3.metric("🎯 Margem", f"{margem:.1f}%")
     m4.metric("🎫 Ticket Médio", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")
 # --- GRÁFICO DE BARRAS (Versão Organizada) ---
    if col_data:
        st.subheader("📊 Evolução de Vendas por Período")
        # Em vez de somar [col_valor], some ['Faturamento_Real']
        df_tempo = df_filtrado.groupby(col_data)['Faturamento_Real'].sum().reset_index()

        fig_barras = px.bar(
            df_tempo, x=col_data, y=col_valor,
            color=col_valor, 
            color_continuous_scale='Blues',
            text_auto='.2s'
        )
        
        # --- FUNÇÃO QUE ARRUMA A BAGUNÇA DO MOUSE (HOVER) ---
        fig_barras.update_traces(
            hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>"
        )
        
        fig_barras.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title=None, yaxis_title=None,
            coloraxis_showscale=False,
            height=400,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    st.markdown("---")
    
    # --- RANKINGS E MIX (Dividido em 2 colunas) ---
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.subheader("🎯 Mix de Categorias")
        fig_rosca = px.pie(
            df_filtrado, values=col_valor, names=col_cat, hole=0.7,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_rosca.update_traces(
            textinfo='percent', 
            pull=[0.03] * len(df_filtrado[col_cat].unique()),
            hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<extra></extra>"
        )
        fig_rosca.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_rosca, use_container_width=True)
        

        with c_right:
         st.subheader("🏆 Performance de Itens")
         tab1, tab2 = st.tabs(["🚀 Top Vendas", "⚠️ Menos Vendidos"])
        
        # 1. Agrupamento e soma real
        # Se col_qtd existir, somamos os valores reais da planilha
        df_perf = df_filtrado.groupby(col_prod).agg({
            col_valor: 'sum',
            col_qtd: 'sum' if col_qtd else 'count' # Se não tiver a coluna, ele conta as ocorrências
        }).reset_index()

        # 2. Renomeando para nomes amigáveis
        df_perf.columns = ['Produto', 'Faturamento Total', 'Qtd Saída']

        # 3. Limpeza: Remove itens com valores zerados ou nomes estranhos
        df_perf = df_perf[df_perf['Faturamento Total'] > 0]
        
        with tab1:
            # Ordena pelos que MAIS faturaram
            top_vendas = df_perf.nlargest(5, 'Faturamento Total')
            
            # Formatação "REAL": Coloca R$ e separa milhares
            st.dataframe(
                top_vendas.style.format({
                    'Faturamento Total': 'R$ {:,.2f}',
                    'Qtd Saída': '{:,.0f} unid.'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        with tab2:
            # Ordena pelos que MENOS faturaram
            bottom_vendas = df_perf.nsmallest(5, 'Faturamento Total')
            
            st.dataframe(
                bottom_vendas.style.format({
                    'Faturamento Total': 'R$ {:,.2f}',
                    'Qtd Saída': '{:,.0f} unid.'
                }),
                use_container_width=True,
                hide_index=True
            )
    # --- BASE DE DADOS AMPLIADA (FORA DAS COLUNAS) ---
    # Note que o código abaixo não tem o 'with c_right' na frente dele
    st.markdown("---")
    st.subheader("📄 Base de Dados Completa")
    
    st.dataframe(
        df_filtrado, 
        use_container_width=True, 
        height=600 # Aumentado para ficar bem grande
    )


    
