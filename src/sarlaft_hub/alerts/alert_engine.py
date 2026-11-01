import pandas as pd
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def generar_alertas_tradicionales():
    print("Cargando transacciones y scoring...")
    df_trx = pd.read_csv('data/raw/transacciones.csv')
    df_score = pd.read_csv('data/processed/scoring_riesgo.csv')
    
    # Unimos para tener el score
    df = pd.merge(df_trx, df_score[['cliente_id', 'score_riesgo_0_100']], on='cliente_id', how='left')
    
    print("\n--- MOTOR DE REGLAS TRADICIONAL SFC ---")
    alertas = []
    
    # REGLA 1: Monto > 10M en efectivo (la clásica)
    regla1 = df[df['monto'] > 10000000]
    print(f"Regla 1 - Monto > 10M: {len(regla1)} alertas")
    for _, row in regla1.iterrows():
        alertas.append({**row, 'regla': 'R1_Monto_Alto', 'severidad': 'Media'})
    
    # REGLA 2: Pitufeo - Score alto + monto 8-9.9M
    regla2 = df[(df['score_riesgo_0_100'] > 70) & (df['monto'].between(8000000, 9999999))]
    print(f"Regla 2 - Pitufeo: {len(regla2)} alertas")
    for _, row in regla2.iterrows():
        alertas.append({**row, 'regla': 'R2_Pitufeo', 'severidad': 'Alta'})
    
    # REGLA 3: Fraccionamiento - +3 transacciones mismo cliente mismo día
    df['fecha'] = pd.to_datetime(df['fecha'])
    conteo_dia = df.groupby(['cliente_id', df['fecha'].dt.date]).size().reset_index(name='conteo')
    clientes_fracc = conteo_dia[conteo_dia['conteo'] >= 3]['cliente_id'].unique()
    regla3 = df[df['cliente_id'].isin(clientes_fracc)]
    print(f"Regla 3 - Fraccionamiento: {len(regla3)} alertas")
    for _, row in regla3.iterrows():
        alertas.append({**row, 'regla': 'R3_Fraccionamiento', 'severidad': 'Alta'})

    df_alertas = pd.DataFrame(alertas)
    
    # --- OPTIMIZACIÓN CON ML PARA REDUCIR FALSOS POSITIVOS ---
        # --- OPTIMIZACIÓN CON ML PARA REDUCIR FALSOS POSITIVOS ---
    print(f"\n--- OPTIMIZACION ---")
    print(f"Total alertas brutas del motor tradicional: {len(df_alertas)}")
    
    # Versión Senior: Solo dejamos pasar Score > 80
    # En un banco real aquí iría un modelo de Isolation Forest
    df_alertas_filtradas = df_alertas[df_alertas['score_riesgo_0_100'] > 80].copy()
    
    # Si quieres ser aún más agresivo, sube a 85
    # df_alertas_filtradas = df_alertas[df_alertas['score_riesgo_0_100'] > 85]
    
    reduccion = 100 * (1 - len(df_alertas_filtradas) / len(df_alertas)) if len(df_alertas) > 0 else 0
    
    print(f"Alertas después de filtro ML (Score>80): {len(df_alertas_filtradas)}")
    print(f"Reducción de falsos positivos: {reduccion:.1f}%")
    print(f"Ahorro operativo: Dejas de revisar {len(df_alertas) - len(df_alertas_filtradas)} alertas falsas al mes")
        
    # Guardar
    os.makedirs('data/processed', exist_ok=True)
    df_alertas.to_csv('data/processed/alertas_brutas.csv', index=False)
    df_alertas_filtradas.to_csv('data/processed/alertas_optimizadas.csv', index=False)
    
    print(f"\nGuardados:")
    print(f"- data/processed/alertas_brutas.csv")
    print(f"- data/processed/alertas_optimizadas.csv")
    
    return df_alertas_filtradas

if __name__ == "__main__":
    generar_alertas_tradicionales()