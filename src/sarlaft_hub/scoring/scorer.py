import pandas as pd
import numpy as np
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.sarlaft_hub.utils.config_loader import load_config
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import xgboost as xgb

def crear_features_riesgo():
    print("Cargando datos...")
    df_cli = pd.read_csv('data/processed/clientes_segmentados.csv')
    df_trx = pd.read_csv('data/raw/transacciones.csv')
    
    print("Creando features transaccionales...")
    agg_trx = df_trx.groupby('cliente_id').agg(
        total_transado=('monto', 'sum'),
        n_transacciones=('monto', 'count'),
        monto_promedio=('monto', 'mean'),
        monto_max=('monto', 'max'),
        monto_std=('monto', 'std'),
        n_sospechosas=('patron_real', lambda x: (x != 'Normal').sum())
    ).reset_index()
    
    agg_trx['monto_std'] = agg_trx['monto_std'].fillna(0)
    
    df = pd.merge(df_cli, agg_trx, on='cliente_id', how='left')
    df = df.fillna(0)
    
    # Ratio clave SARLAFT
    df['ratio_trans_ingreso'] = df['total_transado'] / (df['ingresos_mensuales'] * 3)
    df['es_riesgo_alto'] = (df['n_sospechosas'] > 0).astype(int)
    
    print(f"Clientes con riesgo alto: {df['es_riesgo_alto'].sum()} de {len(df)}")
    return df

def entrenar_scoring():
    df = crear_features_riesgo()
    
    features = ['edad', 'log_ingresos', 'antiguedad_meses', 'riesgo_num', 'es_pep', 
                'es_extranjero', 'segmento', 'total_transado', 'n_transacciones', 
                'monto_promedio', 'monto_max', 'monto_std', 'ratio_trans_ingreso']
    
    X = df[features]
    y = df['es_riesgo_alto']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    print(f"\nEntrenando XGBoost...")
    model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("\nReporte de clasificacion:")
    print(classification_report(y_test, y_pred))
    
    df['prob_riesgo'] = model.predict_proba(X)[:, 1]
    df['score_riesgo_0_100'] = (df['prob_riesgo'] * 100).round(0).astype(int)
    
    os.makedirs('data/processed', exist_ok=True)
    df[['cliente_id', 'nombre', 'segmento', 'riesgo_base', 'score_riesgo_0_100', 'prob_riesgo', 'es_riesgo_alto']].to_csv('data/processed/scoring_riesgo.csv', index=False)
    
    print(f"\nScoring guardado en data/processed/scoring_riesgo.csv")
    print(df[['cliente_id', 'score_riesgo_0_100', 'riesgo_base']].head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    entrenar_scoring()