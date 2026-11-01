import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os
import sys

# Cargar config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from config_loader import load_config

def segmentar_clientes():
    cfg = load_config()
    k = cfg['sarlaft']['segmentos_k']
    
    print(f"Cargando clientes...")
    df = pd.read_csv('data/raw/clientes.csv')
    
    # Feature Engineering para SARLAFT
    print("Preparando features de riesgo...")
    df['log_ingresos'] = np.log1p(df['ingresos_mensuales'])
    
    # Convertimos riesgo_base a número para el modelo
    mapa_riesgo = {'Bajo': 1, 'Medio': 2, 'Alto': 3}
    df['riesgo_num'] = df['riesgo_base'].map(mapa_riesgo)
    
    # Features que usará K-Means
    features = ['edad', 'log_ingresos', 'antiguedad_meses', 'riesgo_num', 'es_pep', 'es_extranjero']
    X = df[features]
    
    # Escalado - OBLIGATORIO en clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"Entrenando K-Means con k={k} (lo que pusimos en config.yaml)...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['segmento'] = kmeans.fit_predict(X_scaled)
    
    # Métrica de calidad
    sil_score = silhouette_score(X_scaled, df['segmento'])
    print(f"\nSilhouette Score: {sil_score:.3f} (mientras más cerca a 1, mejor)")
    
    print("\nDistribución de clientes por segmento:")
    print(df['segmento'].value_counts().sort_index())
    
    # Perfil de cada segmento para el informe a la SFC
    print("\nPerfil de riesgo por segmento:")
    perfil = df.groupby('segmento').agg({
        'ingresos_mensuales': 'mean',
        'edad': 'mean',
        'es_pep': 'sum',
        'es_extranjero': 'sum',
        'cliente_id': 'count'
    }).round(2)
    print(perfil)
    
    # Guardar
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/processed/clientes_segmentados.csv', index=False)
    perfil.to_csv('data/processed/perfil_segmentos.csv')
    print(f"\nGuardado en data/processed/clientes_segmentados.csv")
    print(f"Perfil guardado en data/processed/perfil_segmentos.csv")
    
    return df

if __name__ == "__main__":
    segmentar_clientes()