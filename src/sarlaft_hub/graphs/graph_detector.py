import pandas as pd
import networkx as nx
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def detectar_redes():
    print("Cargando datos para grafo...")
    df_trx = pd.read_csv('data/raw/transacciones.csv')
    df_score = pd.read_csv('data/processed/scoring_riesgo.csv')
    df_cli = pd.read_csv('data/processed/clientes_segmentados.csv')
    
    df_sos = df_trx[df_trx['patron_real'] != 'Normal'].copy()
    df_sos = pd.merge(df_sos, df_score[['cliente_id', 'score_riesgo_0_100']], on='cliente_id', how='left')
    df_sos = pd.merge(df_sos, df_cli[['cliente_id', 'municipio']], on='cliente_id', how='left')
    
    print(f"Transacciones sospechosas para grafo: {len(df_sos)}")
    
    G = nx.Graph()
    
    for _, row in df_score.iterrows():
        G.add_node(row['cliente_id'], score=int(row['score_riesgo_0_100']), riesgo=row['riesgo_base'])
    
    print("Construyendo aristas por co-ocurrencia (mismo dia + mismo municipio)...")
    df_sos['fecha'] = pd.to_datetime(df_sos['fecha']).dt.date
    
    aristas_creadas = 0
    for (fecha, municipio), grupo in df_sos.groupby(['fecha', 'municipio']):
        clientes_en_grupo = grupo['cliente_id'].unique()
        if len(clientes_en_grupo) > 1:
            for i in range(len(clientes_en_grupo)):
                for j in range(i+1, len(clientes_en_grupo)):
                    c1, c2 = clientes_en_grupo[i], clientes_en_grupo[j]
                    # Si no existe la arista, la creamos. Sin peso, simple.
                    if not G.has_edge(c1, c2):
                        G.add_edge(c1, c2, fecha=str(fecha), municipio=municipio)
                        aristas_creadas += 1
    
    print(f"Grafo creado: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    
    if G.number_of_edges() > 0:
        componentes = list(nx.connected_components(G))
        print(f"Redes detectadas (componentes conexos): {len(componentes)}")
        
        red_mas_grande = max(componentes, key=len)
        print(f"Red mas grande: {len(red_mas_grande)} clientes conectados")
        print(f"Clientes en red sospechosa: {list(red_mas_grande)[:10]}")
        
        centralidad = nx.degree_centrality(G)
        top_cabecillas = sorted(centralidad.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\nTop 5 posibles cabecillas:")
        for cliente, cent in top_cabecillas:
            print(f"  {cliente} - centralidad {cent:.3f} - Score {G.nodes[cliente].get('score')}")
        
        os.makedirs('data/processed', exist_ok=True)
        
        redes = []
        for idx, comp in enumerate(componentes):
            if len(comp) > 2:
                for cliente in comp:
                    redes.append({'red_id': idx, 'cliente_id': cliente, 'tamano_red': len(comp), 'score': G.nodes[cliente].get('score')})
        
        df_redes = pd.DataFrame(redes)
        if not df_redes.empty:
            df_redes.to_csv('data/processed/redes_sospechosas.csv', index=False)
            print(f"\nRedes guardadas en data/processed/redes_sospechosas.csv - {len(df_redes)} registros")
        
        nx.write_gexf(G, 'data/processed/grafo_sarlaft.gexf')
        print("Grafo exportado a data/processed/grafo_sarlaft.gexf (abrible en Gephi)")
    else:
        print("No se encontraron conexiones suficientes")

if __name__ == "__main__":
    detectar_redes()