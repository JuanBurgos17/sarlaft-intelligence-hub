import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import os
import sys

# Para poder leer el config.yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from config_loader import load_config

fake = Faker('es_CO')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generar_clientes(n_clientes=5000):
    clientes = []
    actividades = ['Asalariado', 'Comerciante', 'Independiente', 'Agricultor', 'Transportador', 'Construccion', 'Servicios']
    municipios = ['Bogota', 'Medellin', 'Cali', 'El Bagre', 'Cucuta', 'Barranquilla', 'Cartagena']
    deptos = ['Antioquia', 'Cundinamarca', 'Valle', 'Norte de Santander', 'Bolivar']
    
    for i in range(n_clientes):
        ingresos = int(np.random.lognormal(mean=15, sigma=0.8))
        es_pep = np.random.choice([0, 1], p=[0.97, 0.03])
        es_extranjero = np.random.choice([0, 1], p=[0.95, 0.05])
        
        riesgo_base = 'Bajo'
        if es_pep == 1 or ingresos > 50000000:
            riesgo_base = 'Alto'
        elif ingresos > 20000000 or es_extranjero == 1:
            riesgo_base = 'Medio'

        clientes.append({
            'cliente_id': f'CLI_{i+1:05d}',
            'nombre': fake.name(),
            'edad': random.randint(18, 75),
            'tipo_cliente': np.random.choice(['Natural', 'Juridica'], p=[0.85, 0.15]),
            'actividad_economica': random.choice(actividades),
            'ingresos_mensuales': ingresos,
            'municipio': random.choice(municipios),
            'departamento': random.choice(deptos),
            'pais': 'Colombia' if es_extranjero == 0 else fake.country(),
            'es_pep': es_pep,
            'es_extranjero': es_extranjero,
            'riesgo_base': riesgo_base,
            'antiguedad_meses': random.randint(1, 120)
        })
    return pd.DataFrame(clientes)

def generar_transacciones(df_clientes, n_trans=50000):
    transacciones = []
    
    for i in range(n_trans):
        cliente = df_clientes.sample(1).iloc[0]
        
        monto = int(np.random.lognormal(mean=13, sigma=1.2))
        tipo = 'Normal'
        
        rnd = random.random()
        if rnd < 0.02:
            monto = random.randint(8000000, 9900000)
            tipo = 'Pitufeo_Sospechoso'
        elif rnd < 0.035:
            monto = random.randint(2000000, 4000000)
            tipo = 'Fraccionamiento_Sospechoso'
        elif rnd < 0.05 and cliente['ingresos_mensuales'] < 3000000:
            monto = random.randint(30000000, 80000000)
            tipo = 'Cambio_Perfil_Sospechoso'

        transacciones.append({
            'transaccion_id': f'TRX_{i+1:06d}',
            'cliente_id': cliente['cliente_id'],
            'fecha': fake.date_between(start_date='-90d', end_date='today'),
            'monto': monto,
            'tipo_transaccion': random.choice(['Consignacion', 'Retiro', 'Transferencia']),
            'canal': random.choice(['Sucursal', 'Digital', 'Cajero', 'Corresponsal']),
            'producto': random.choice(['Ahorros', 'Corriente', 'Nomina']),
            'patron_real': tipo
        })
    
    return pd.DataFrame(transacciones)

if __name__ == "__main__":
    cfg = load_config()
    print(f"Generando {cfg['data']['n_clientes']} clientes...")
    df_cli = generar_clientes(cfg['data']['n_clientes'])
    
    print(f"Generando {cfg['data']['n_transacciones']} transacciones...")
    df_trx = generar_transacciones(df_cli, cfg['data']['n_transacciones'])

    os.makedirs('data/raw', exist_ok=True)
    df_cli.to_csv('data/raw/clientes.csv', index=False)
    df_trx.to_csv('data/raw/transacciones.csv', index=False)
    
    print("Listo!")
    print(f"Clientes: {df_cli.shape}")
    print(f"Transacciones: {df_trx.shape}")
    print("\nConteo de patrones:")
    print(df_trx['patron_real'].value_counts())