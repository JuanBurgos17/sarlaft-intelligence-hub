# SARLAFT Intelligence Hub

Plataforma analítica End-to-End para Unidad de Cumplimiento bajo normativa SFC Colombia.

Este proyecto simula la estrategia analítica para prevenir LA/FT con:
- Segmentación de factores de riesgo
- Scoring de riesgo individual
- Motor de alertas híbrido (reglas + ML)
- Análisis de grafos para pitufeo
- Screening de listas restrictivas
- Dashboard y reportería UIAF
SARLAFT Intelligence Hub - Plataforma Analítica End-to-End
Plataforma para Unidad de Cumplimiento bajo Circular Externa 027 de 2020 - SFC Colombia

Proyecto Científico de Datos SARLAFT (LA/FT)

Simula la operación completa de una unidad de cumplimiento: desde segmentación hasta reporte ROS UIAF.
# Stack
Python 3.10, Scikit-learn, XGBoost, NetworkX, Neo4j, Gephi.

# Resumen
Se diseñó una estrategia analítica que procesa 5000 clientes y 50000 transacciones sintéticas con patrones reales de lavado:

- Segmentación: K-Means k=5 aisló 100% PEPs (146 clientes) y 245 extranjeros
- Scoring: XGBoost 0-100 con 87% accuracy, 86% precision, 72% recall | 1705 clientes en riesgo alto
- Motor de Alertas Híbrido: 2778 alertas brutas → 1796 optimizadas con 35.3% reducción usando score>80 = 327 horas/mes ahorradas
- Grafos: 5000 nodos, 3522 aristas, red principal de 191 clientes (posible red de testaferros), Top 5 cabecillas Score 98-99
- Screening OFAC/ONU: 160 registros (150 fake + 10 trampa) → 13 coincidencias detectadas
- Reporte ROS UIAF: 5 casos críticos Score 100 con tipología Pitufeo + Red Testaferros.

# KPIs del Dashboard
Métrica	            Resultado
Total Clientes	    5000
Alertas Optimizadas	1796
Riesgo Alto (>80)	1705
Redes Detectadas	126
Coincidencias OFAC	13
Red Principal	    191 nodos / 3522 relaciones

# Metodologia

Paso 1 - Generador Sintético: 5000 clientes (13 cols) + 50000 transacciones (8 cols). Patrones: Normal 47500, Pitufeo_Sospechoso 1038, Fraccionamiento 720, Cambio_Perfil 356.

Paso 2 - Segmentación K=5: Features: edad, log_ingresos, antigüedad, riesgo_num, es_pep, es_extranjero. Perfil: Seg 0: 1716 bajo riesgo, Seg 1: 245 extranjeros, Seg 2: 146 PEPs (100% aislados).

Paso 3 - Scoring 0-100: Features: total_transado, n_transacciones, monto_promedio, max, std, n_sospechosas, ratio_trans_ingreso.

Paso 4 - Motor Alertas: R1 581, R2 1122, R3 1075. Optimización score>80 redujo de 2778 a 1796.

Paso 5 - Grafos: 3520 componentes, red más grande 191. Visualización con matplotlib: rojo>90, naranja>70, celeste bajo riesgo. Núcleo denso = testaferros, sub-redes = pitufeo distribuido.

Paso 6 - Screening: 13 coincidencias OFAC SDN por narcotráfico.

Paso 7 - Dashboard + ROS: Streamlit + Plotly con filtros ejecutivos y reporte UIAF listo para radicar.

# Detección de Redes
Red principal detectada de 191 clientes con 3522 relaciones - posible red de testaferros. Núcleo denso central con sub-redes y cadenas de layering (pitufeo distribuido).

# Cumplimiento Normativo
Circular Externa 027 de 2020 SFC: Capitulo X - SARLAFT 4.0
UIAF: Generación automática ROS con tipología, sustento y acción recomendada (bloqueo preventivo)
Debida Diligencia: Segmentación PEP, screening listas restrictivas, scoring individual

# Autor: Juan Burgos - Proyecto Portafolio Científico de Datos 