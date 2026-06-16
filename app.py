import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="🔥 Queimados Brasil 2025",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Mapeamentos UF ─────────────────────────────────────────────────────────────
UF_CTQ = {
    'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPÁ': 'AP', 'AMAZONAS': 'AM',
    'BAHIA': 'BA', 'CEARÁ': 'CE', 'DISTRITO FEDERAL': 'DF',
    'ESPÍRITO SANTO': 'ES', 'GOIÁS': 'GO', 'MARANHÃO': 'MA',
    'MATO GROSSO': 'MT', 'MATO GROSSO DO SUL': 'MS', 'MINAS GERAIS': 'MG',
    'PARANÁ': 'PR', 'PARAÍBA': 'PB', 'PARÁ': 'PA', 'PERNAMBUCO': 'PE',
    'PIAUÍ': 'PI', 'RIO GRANDE DO NORTE': 'RN', 'RIO GRANDE DO SUL': 'RS',
    'RIO DE JANEIRO': 'RJ', 'RONDÔNIA': 'RO', 'RORAIMA': 'RR',
    'SANTA CATARINA': 'SC', 'SERGIPE': 'SE', 'SÃO PAULO': 'SP',
    'TOCANTINS': 'TO',
}

UF_GRAF = {
    'ACRE': 'AC', 'ALAGOA': 'AL', 'AMAPÁ': 'AP', 'AMAZONA': 'AM',
    'BAHIA': 'BA', 'CEARÁ': 'CE', 'D. FEDERAL': 'DF', 'E. SANTO': 'ES',
    'GOIÁS': 'GO', 'MARANHÃO': 'MA', 'M. GROSSO': 'MT', 'M. G. SUL': 'MS',
    'M. GERAIS': 'MG', 'PARANÁ': 'PR', 'PARAIBA': 'PB', 'PARÁ': 'PA',
    'PERNAMBUCO': 'PE', 'PIAUÍ': 'PI', 'R. G. NORTE': 'RN',
    'R. G. SUL': 'RS', 'R. DE JANEIRO': 'RJ', 'RONDONIA': 'RO',
    'RORAIMA': 'RR', 'S. CATARINA': 'SC', 'SERGIPE': 'SE',
    'S. PAULO': 'SP', 'TOCANTINS': 'TO',
}

UF_NOME = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal',
    'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão',
    'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
    'PR': 'Paraná', 'PB': 'Paraíba', 'PA': 'Pará', 'PE': 'Pernambuco',
    'PI': 'Piauí', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
    'RJ': 'Rio de Janeiro', 'RO': 'Rondônia', 'RR': 'Roraima',
    'SC': 'Santa Catarina', 'SE': 'Sergipe', 'SP': 'São Paulo',
    'TO': 'Tocantins',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Carregamento e cache dos dados ────────────────────────────────────────────
@st.cache_data
def load_ctq():
    df = pd.read_excel(os.path.join(BASE_DIR, 'ctq.xlsx'))
    df.columns = ['Estado', 'CTQ']
    df['UF']   = df['Estado'].map(UF_CTQ)
    df['Nome'] = df['UF'].map(UF_NOME)
    return df


@st.cache_data
def load_faixa_etaria():
    df = pd.read_excel(os.path.join(BASE_DIR, 'Faixa Etaria (1).xlsx'), header=1)
    df.columns = ['Faixa_Etaria', 'Feminino', 'Masculino']
    df['Feminino']  = pd.to_numeric(df['Feminino'],  errors='coerce')
    df['Masculino'] = pd.to_numeric(df['Masculino'], errors='coerce')
    df = df.dropna(subset=['Faixa_Etaria', 'Feminino', 'Masculino'])
    df['Total'] = df['Feminino'] + df['Masculino']
    return df


@st.cache_data
def load_internacoes():
    df = pd.read_excel(os.path.join(BASE_DIR, 'GRAFICO2.xlsx'))
    df.columns = ['Estado', 'Internacao', 'Morte']
    df['Morte']    = pd.to_numeric(df['Morte'], errors='coerce').fillna(0).astype(int)
    df['UF']       = df['Estado'].map(UF_GRAF)
    df['Nome']     = df['UF'].map(UF_NOME)
    return df


@st.cache_data
def load_geojson():
    with open(os.path.join(BASE_DIR, 'brazil_states.geojson'), 'r', encoding='utf-8') as f:
        return json.load(f)


df_ctq    = load_ctq()
df_fe     = load_faixa_etaria()
df_intern = load_internacoes()
geojson   = load_geojson()

# Merge: adiciona coluna CTQ ao dataframe de internações (para o mapa)
df_mapa = df_intern.merge(df_ctq[['UF', 'CTQ']], on='UF', how='left')

# ── CSS Customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    h1 { color: #c0392b; }
    [data-testid="stMetricValue"] { color: #c0392b; font-size: 1.9rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("# 🔥 Dashboard de Queimados — Brasil 2025")
st.markdown(
    "*Internações, óbitos e Centros de Tratamento de Queimados (CTQ) "
    "por estado — Fonte: Ministério da Saúde*"
)
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_intern  = int(df_intern['Internacao'].sum())
total_morte   = int(df_intern['Morte'].sum())
total_ctq     = int(df_ctq['CTQ'].sum())
taxa_mort     = round(total_morte / total_intern * 100, 2)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🏥 Total de Internações",  f"{total_intern:,}".replace(',', '.'))
c2.metric("💀 Total de Óbitos",       f"{total_morte:,}".replace(',', '.'))
c3.metric("🏢 CTQs no Brasil",        total_ctq)
c4.metric("📊 Taxa de Mortalidade",   f"{taxa_mort} %")
st.divider()

# ── Abas ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Mapa do Brasil",
    "📊 Internações e Óbitos por Estado",
    "👥 Faixa Etária",
    "🏢 Centros de Tratamento (CTQ)",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — MAPA DO BRASIL (choropleth interativo)
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Distribuição Geográfica por Estado")

    col_ctrl, col_map = st.columns([1, 3])

    with col_ctrl:
        variavel = st.radio(
            "Variável exibida no mapa:",
            options=["Internações", "Óbitos", "CTQs"],
            index=0,
        )
        col_var   = {"Internações": "Internacao", "Óbitos": "Morte", "CTQs": "CTQ"}[variavel]
        label_var = variavel

        st.markdown("---")
        st.markdown(f"**🏆 Top 5 — {label_var}:**")
        top5 = df_mapa.nlargest(5, col_var)[['Nome', col_var]]
        for _, row in top5.iterrows():
            st.markdown(f"🔸 **{row['Nome']}**: {int(row[col_var])}")

    with col_map:
        paletas = {"Internacao": "Reds", "Morte": "YlOrRd", "CTQ": "Blues"}

        fig_map = px.choropleth(
            df_mapa,
            geojson=geojson,
            locations='UF',
            featureidkey='properties.sigla',
            color=col_var,
            color_continuous_scale=paletas[col_var],
            hover_name='Nome',
            hover_data={
                'Internacao': True,
                'Morte':      True,
                'CTQ':        True,
                'UF':         False,
            },
            labels={
                'Internacao': 'Internações',
                'Morte':      'Óbitos',
                'CTQ':        'CTQs',
                col_var:      label_var,
            },
            title=f"{label_var} por Estado — Brasil 2025",
        )
        fig_map.update_geos(fitbounds='locations', visible=False)
        fig_map.update_layout(
            height=520,
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_colorbar=dict(title=label_var),
        )
        st.plotly_chart(fig_map, width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — GRÁFICO DE BARRAS: INTERNAÇÕES E ÓBITOS POR ESTADO
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Internações e Óbitos por Estado — Brasil 2025")

    c_ord, c_exib, c_modo = st.columns(3)
    with c_ord:
        ordem = st.selectbox(
            "Ordenar por:",
            ["Internações ↓", "Internações ↑", "Óbitos ↓", "Estado (A → Z)"],
        )
    with c_exib:
        exibir = st.multiselect(
            "Exibir:",
            ["Internações", "Óbitos"],
            default=["Internações", "Óbitos"],
        )
    with c_modo:
        modo = st.radio("Modo das barras:", ["Agrupado", "Empilhado"], horizontal=True)

    ord_map = {
        "Internações ↓":   ("Internacao", False),
        "Internações ↑":   ("Internacao", True),
        "Óbitos ↓":        ("Morte",      False),
        "Estado (A → Z)":  ("Nome",       True),
    }
    col_ord, asc = ord_map[ordem]
    df_sorted = df_intern.sort_values(col_ord, ascending=asc)

    fig_bar2 = go.Figure()
    if "Internações" in exibir:
        fig_bar2.add_trace(go.Bar(
            name='Internações',
            x=df_sorted['Nome'],
            y=df_sorted['Internacao'],
            marker_color='#e74c3c',
            hovertemplate='<b>%{x}</b><br>Internações: %{y:,}<extra></extra>',
        ))
    if "Óbitos" in exibir:
        fig_bar2.add_trace(go.Bar(
            name='Óbitos',
            x=df_sorted['Nome'],
            y=df_sorted['Morte'],
            marker_color='#2c3e50',
            hovertemplate='<b>%{x}</b><br>Óbitos: %{y:,}<extra></extra>',
        ))

    fig_bar2.update_layout(
        barmode='group' if modo == "Agrupado" else 'stack',
        xaxis_title='Estado',
        yaxis_title='Quantidade',
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(tickangle=-45),
    )
    st.plotly_chart(fig_bar2, width='stretch')

    with st.expander("📋 Ver tabela completa"):
        df_tab2 = df_intern[['Nome', 'Internacao', 'Morte']].copy()
        df_tab2.columns = ['Estado', 'Internações', 'Óbitos']
        df_tab2['Mortalidade (%)'] = (
            df_tab2['Óbitos'] / df_tab2['Internações'] * 100
        ).round(2)
        df_tab2 = df_tab2.sort_values('Internações', ascending=False).reset_index(drop=True)
        st.dataframe(df_tab2, width='stretch', hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — FAIXA ETÁRIA
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Internações por Faixa Etária e Sexo — 2025")

    c_tipo, c_sexo, c_tot = st.columns(3)
    with c_tipo:
        tipo_graf = st.radio("Tipo de gráfico:", ["Barras", "Linha"], horizontal=True)
    with c_sexo:
        sexo_sel = st.multiselect(
            "Sexo:", ["Feminino", "Masculino"],
            default=["Feminino", "Masculino"],
        )
    with c_tot:
        mostrar_total = st.checkbox("Mostrar linha de Total", value=True)

    cores = {'Feminino': '#e91e8c', 'Masculino': '#1565c0', 'Total': '#ff6b35'}
    fig_fe = go.Figure()

    for s in sexo_sel:
        if tipo_graf == "Barras":
            fig_fe.add_trace(go.Bar(
                name=s,
                x=df_fe['Faixa_Etaria'],
                y=df_fe[s],
                marker_color=cores[s],
                hovertemplate=f'<b>{s}</b> | %{{x}}<br>Internações: %{{y:,}}<extra></extra>',
            ))
        else:
            fig_fe.add_trace(go.Scatter(
                name=s,
                x=df_fe['Faixa_Etaria'],
                y=df_fe[s],
                mode='lines+markers',
                line=dict(color=cores[s], width=2),
                marker=dict(size=7),
                hovertemplate=f'<b>{s}</b> | %{{x}}<br>Internações: %{{y:,}}<extra></extra>',
            ))

    if mostrar_total:
        fig_fe.add_trace(go.Scatter(
            name='Total',
            x=df_fe['Faixa_Etaria'],
            y=df_fe['Total'],
            mode='lines+markers',
            line=dict(color=cores['Total'], width=2, dash='dash'),
            marker=dict(size=7),
            hovertemplate='<b>Total</b> | %{x}<br>Internações: %{y:,}<extra></extra>',
        ))

    fig_fe.update_layout(
        barmode='group',
        xaxis_title='Faixa Etária',
        yaxis_title='Número de Internações',
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    st.plotly_chart(fig_fe, width='stretch')

    with st.expander("📋 Ver tabela completa"):
        df_tab3 = df_fe[['Faixa_Etaria', 'Feminino', 'Masculino', 'Total']].copy()
        df_tab3.columns = ['Faixa Etária', 'Feminino', 'Masculino', 'Total']
        df_tab3['% Feminino']  = (df_tab3['Feminino']  / df_tab3['Total'] * 100).round(1)
        df_tab3['% Masculino'] = (df_tab3['Masculino'] / df_tab3['Total'] * 100).round(1)
        st.dataframe(df_tab3, width='stretch', hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CTQ
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Centros de Tratamento de Queimados (CTQ) por Estado")

    c_filt, c_ori = st.columns(2)
    with c_filt:
        apenas_com = st.checkbox("Mostrar apenas estados que possuem CTQ", value=False)
    with c_ori:
        orientacao = st.radio("Orientação das barras:", ["Vertical", "Horizontal"], horizontal=True)

    df_ctq_plot = df_ctq[df_ctq['CTQ'] > 0].copy() if apenas_com else df_ctq.copy()
    df_ctq_plot = df_ctq_plot.sort_values('CTQ', ascending=(orientacao == "Horizontal"))

    if orientacao == "Vertical":
        fig_ctq = px.bar(
            df_ctq_plot,
            x='Nome', y='CTQ',
            color='CTQ',
            color_continuous_scale='Blues',
            text='CTQ',
            labels={'Nome': 'Estado', 'CTQ': 'Nº de CTQs'},
            height=500,
        )
        fig_ctq.update_traces(textposition='outside')
        fig_ctq.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False,
        )
    else:
        fig_ctq = px.bar(
            df_ctq_plot,
            y='Nome', x='CTQ',
            orientation='h',
            color='CTQ',
            color_continuous_scale='Blues',
            text='CTQ',
            labels={'Nome': 'Estado', 'CTQ': 'Nº de CTQs'},
            height=580,
        )
        fig_ctq.update_traces(textposition='outside')
        fig_ctq.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False,
        )

    st.plotly_chart(fig_ctq, width='stretch')

    st.info(
        f"🏢 O Brasil possui **{total_ctq} CTQs** distribuídos em "
        f"**{int((df_ctq['CTQ'] > 0).sum())} estados**. "
        f"São Paulo concentra sozinho **{int(df_ctq.loc[df_ctq['UF']=='SP','CTQ'].values[0])} unidades**."
    )

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center; color:#aaa; font-size:0.82rem;">'
    'Fonte dos dados: Ministério da Saúde &nbsp;|&nbsp; '
    'Dashboard desenvolvido com Streamlit + Plotly'
    '</p>',
    unsafe_allow_html=True,
)
