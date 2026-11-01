import os

estructura = [
    "config",
    "data/raw",
    "data/processed",
    "data/external",
    "src/sarlaft_hub/data_generator",
    "src/sarlaft_hub/segmentation",
    "src/sarlaft_hub/scoring",
    "src/sarlaft_hub/alerts",
    "src/sarlaft_hub/graphs",
    "src/sarlaft_hub/screening",
    "src/sarlaft_hub/reporting",
    "src/sarlaft_hub/utils",
    "notebooks",
    "tests",
    "dashboards",
    "docs"
]

for carpeta in estructura:
    os.makedirs(carpeta, exist_ok=True)
    # Creamos el .gitkeep de forma segura
    with open(os.path.join(carpeta, ".gitkeep"), "w") as f:
        pass

# archivos __init__.py para que python entienda que son paquetes
for root, dirs, files in os.walk("src"):
    if "sarlaft_hub" in root or root == "src":
        with open(os.path.join(root, "__init__.py"), "w") as f:
            pass

print("Estructura creada correctamente")