import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="SARLAFT Intelligence Hub", layout="wide", page_icon="🛡️")

st.title("SARLAFT Intelligence Hub - Dashboard Ejecutivo (Simulación)")
st.markdown("Proyecto portafolio para vacante Científico de Datos SARLAFT - Cumplimiento Circular Externa 027 de 2020 SFC ")

# Cargar datos
@st.cache_data
def load_data():
    base = "data/processed"
    try:
        clientes = pd.read_csv(f"{base}/clientes_segmentados.csv")
        scoring = pd.read_csv(f"{base}/scoring_riesgo.csv")
        alertas = pd.read_csv(f"{base}/alertas_optimizadas.csv")
        redes = pd.read_csv(f"{base}/redes_sospechosas.csv")
        ofac = pd.read_csv(f"{base}/coincidencias_ofac.csv")
        perfil = pd.read_csv(f"{base}/perfil_segmentos.csv")
        return clientes, scoring, alertas, redes, ofac, perfil
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None, None, None, None, None

clientes, scoring, alertas, redes, ofac, perfil = load_data()

if clientes is not None:
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    # Detectar columna score para KPIs
    score_cols = [c for c in scoring.columns if 'score' in c.lower() or 'prob' in c.lower()]
    s_col = next((c for c in scoring.columns if '0_100' in c), score_cols[0] if score_cols else scoring.columns[0])
    n_alto = len(scoring[scoring[s_col] > 80])
    col1.metric("Total Clientes", len(clientes))
    col2.metric("Alertas Optimizadas", len(alertas))
    col3.metric("Riesgo Alto (>80)", n_alto)
    col4.metric("Redes Detectadas", redes['red_id'].nunique() if 'red_id' in redes.columns else len(redes))
    col5.metric("Coincidencias OFAC", len(ofac))

    st.divider()

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribución de Score de Riesgo 0-100")
        col_score = next((c for c in scoring.columns if '0_100' in c), [c for c in scoring.columns if 'score' in c.lower()][0])
        fig = px.histogram(scoring, x=col_score, nbins=20, color_discrete_sequence=['#d62728'])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Perfil de Segmentos (K-Means k=5)")
        st.dataframe(perfil, use_container_width=True)

    with c2:
        st.subheader("Alertas por Regla")
        if 'regla' in alertas.columns:
            fig2 = px.bar(alertas['regla'].value_counts().reset_index(), x='regla', y='count', color='regla')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Red Principal Detectada (191 nodos)")
        if os.path.exists("dashboards/red_principal_sarlaft.png"):
            st.image("dashboards/red_principal_sarlaft.png", caption="Núcleo denso = posible estructura de testaferros", use_container_width=True)

    st.divider()
    st.subheader("Top 10 Clientes Más Riesgosos - Prioridad Investigación")
    # detectar columna de score robusta
    score_candidates = [c for c in scoring.columns if 'score' in c.lower() or 'riesgo' in c.lower()]
    # priorizar la de 0_100
    score_col = next((c for c in scoring.columns if '0_100' in c), score_candidates[0] if score_candidates else scoring.columns[0])
    top = scoring.sort_values(score_col, ascending=False).head(10)
    # merge con clientes para nombre
    top = pd.merge(top, clientes[['cliente_id','nombre','segmento']], on='cliente_id', how='left')
    st.dataframe(top, use_container_width=True)

    st.subheader("Coincidencias Listas Restrictivas OFAC/ONU")
    st.dataframe(ofac, use_container_width=True)

    st.info(" Optimización: Motor de alertas redujo 35.3% de falsos positivos usando score>80, ahorrando 327 horas/mes de análisis operativo")