import networkx as nx
import matplotlib.pyplot as plt
import os

print("Cargando grafo...")
G = nx.read_gexf('data/processed/grafo_sarlaft.gexf')

# Nos quedamos solo con la red más grande de 191 clientes, si no es imposible ver nada
componentes = list(nx.connected_components(G))
red_grande = max(componentes, key=len)
G_grande = G.subgraph(red_grande)

print(f"Visualizando red principal: {len(G_grande.nodes())} nodos, {len(G_grande.edges())} aristas")

plt.figure(figsize=(12, 12))

# Colores por score de riesgo
colores = []
for n in G_grande.nodes():
    score = G_grande.nodes[n].get('score', 0)
    if score > 90:
        colores.append('red') # alto riesgo
    elif score > 70:
        colores.append('orange')
    else:
        colores.append('lightblue')

nx.draw(G_grande, with_labels=False, node_color=colores, node_size=80, edge_color='gray', alpha=0.6)

plt.title(f"Red SARLAFT Principal - {len(red_grande)} clientes conectados - Pitufeo", fontsize=14)
os.makedirs('dashboards', exist_ok=True)
plt.savefig('dashboards/red_principal_sarlaft.png', dpi=300, bbox_inches='tight')
print("Imagen guardada en dashboards/red_principal_sarlaft.png")
plt.show()