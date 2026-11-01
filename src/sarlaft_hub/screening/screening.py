import pandas as pd
import random
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import sin autolink
import importlib
faker_module = importlib.import_module('faker')
FakerClass = getattr(faker_module, 'Faker')
fake = FakerClass('es_CO')

def generar_lista_ofac_fake(n=150):
    print(f"Generando lista restrictiva simulada OFAC/ONU con {n} registros...")
    lista = []
    for i in range(n):
        lista.append({
            'nombre_ofac': fake.name(),
            'tipo_lista': random.choice(['OFAC SDN', 'ONU', 'OFAC Clinton']),
            'motivo': random.choice(['Narcotrafico', 'Terrorismo', 'Corrupcion'])
        })
    df_cli = pd.read_csv('data/processed/clientes_segmentados.csv')
    clientes_trampa = df_cli.sample(10, random_state=42)['nombre'].tolist()
    for nombre in clientes_trampa:
        lista.append({'nombre_ofac': nombre, 'tipo_lista': 'OFAC SDN', 'motivo': 'Narcotrafico'})
    return pd.DataFrame(lista)

def screening_clientes():
    df_cli = pd.read_csv('data/processed/clientes_segmentados.csv')
    df_lista = generar_lista_ofac_fake()
    print(f"Clientes a revisar: {len(df_cli)}")
    print(f"Registros en lista restrictiva: {len(df_lista)}")
    print("\nEjecutando cruce...")
    matches = pd.merge(df_cli, df_lista, left_on='nombre', right_on='nombre_ofac', how='inner')
    print(f"Coincidencias encontradas: {len(matches)}")
    if len(matches) > 0:
        print("\nTop coincidencias:")
        print(matches[['cliente_id', 'nombre', 'tipo_lista', 'motivo']].head(10).to_string(index=False))
        os.makedirs('data/processed', exist_ok=True)
        matches.to_csv('data/processed/coincidencias_ofac.csv', index=False)
        print(f"\nGuardado en data/processed/coincidencias_ofac.csv")
    return matches

if __name__ == "__main__":
    screening_clientes()