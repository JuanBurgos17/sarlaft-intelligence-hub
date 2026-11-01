import pandas as pd
import os
from datetime import datetime

def generar_reporte_ros():
    print("Generando Reporte ROS UIAF simulado...")
    base = "data/processed"
    clientes = pd.read_csv(f"{base}/clientes_segmentados.csv")
    scoring = pd.read_csv(f"{base}/scoring_riesgo.csv")
    alertas = pd.read_csv(f"{base}/alertas_optimizadas.csv")
    redes = pd.read_csv(f"{base}/redes_sospechosas.csv")
    ofac = pd.read_csv(f"{base}/coincidencias_ofac.csv")

    print(f"Columnas en scoring: {list(scoring.columns)}")
    
    # Detectar columna de score de forma robusta
    posibles = [c for c in scoring.columns if 'score' in c.lower() or 'riesgo' in c.lower() or 'prob' in c.lower()]
    # Filtrar solo numericas
    for col in posibles:
        try:
            if pd.api.types.is_numeric_dtype(scoring[col]):
                score_col = col
                break
        except:
            continue
    else:
        # Si no encuentra, usa la segunda columna numerica
        numeric_cols = scoring.select_dtypes(include='number').columns.tolist()
        score_col = numeric_cols[0] if numeric_cols else scoring.columns[1]
    
    print(f"Usando columna de score: {score_col}")

    top_ros = scoring.sort_values(score_col, ascending=False).head(5)
    top_ros = pd.merge(top_ros, clientes, on='cliente_id', how='left')
    
    reporte = []
    for _, row in top_ros.iterrows():
        cid = row['cliente_id']
        n_alertas = len(alertas[alertas['cliente_id'] == cid]) if 'cliente_id' in alertas.columns else 0
        en_red = cid in redes['cliente_id'].values if 'cliente_id' in redes.columns else False
        en_ofac = cid in ofac['cliente_id'].values if 'cliente_id' in ofac.columns else False
        
        reporte.append({
            'fecha_reporte': datetime.now().strftime("%Y-%m-%d"),
            'cliente_id': cid,
            'nombre': row.get('nombre', ''),
            'score_riesgo': row[score_col],
            'n_alertas': n_alertas,
            'en_red_sospechosa': en_red,
            'en_lista_ofac': en_ofac,
            'tipologia': 'Pitufeo + Red testaferros' if en_red else 'Pitufeo',
            'accion': 'Bloqueo y reporte UIAF inmediato' if (row[score_col] > 85 or en_ofac) else 'Investigacion reforzada',
            'norma': 'Circular Externa 027 de 2020 SFC'
        })
    
    df_ros = pd.DataFrame(reporte)
    df_ros.to_csv("data/processed/ROS_UIAF_reporte.csv", index=False)
    print("\n--- REPORTE ROS GENERADO ---")
    print(df_ros.to_string(index=False))
    print("\nGuardado en: data/processed/ROS_UIAF_reporte.csv")

if __name__ == "__main__":
    generar_reporte_ros()