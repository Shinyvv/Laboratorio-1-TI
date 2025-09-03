import pandas as pd
import numpy as np
import seaborn as sns
from scipy.interpolate import griddata

import matplotlib.pyplot as plt

def generate_wifi_heatmap():
    # Coordenadas de los puntos de medición (AP en el origen 0,0)
    locations = {
        'AP': (0, 0),
        'dump01': (-5, -1),  # 5m oeste, 1m sur
        'dump02': (4, -1),   # 4m este, 1m sur  
        'dump03': (-5, 1),   # 5m oeste, 1m norte
        'dump04': (-7, -3)   # 7m oeste, 3m sur
    }
    
    # Cargar los archivos CSV
    csv_files = [
        'ArchivosCSV/dump-01.csv',
        'ArchivosCSV/dump-02.csv',
        'ArchivosCSV/dump-03.csv',
        'ArchivosCSV/dump-04.csv'
    ]
    dump_names = ['dump01', 'dump02', 'dump03', 'dump04']
    
    # Buscar la potencia de la red fh_a88c80 en cada archivo
    powers = []
    coordinates = []
    
    for i, csv_file in enumerate(csv_files):
        try:
            df = pd.read_csv(csv_file, delimiter=',')
            # Limpiar espacios extra en nombres de columnas
            df.columns = df.columns.str.strip()
            # Limpiar espacios extra en los valores de las columnas relevantes
            if 'ESSID' in df.columns:
                df['ESSID'] = df['ESSID'].astype(str).str.strip()
            if 'Power' in df.columns:
                df['Power'] = df['Power'].astype(str).str.strip()
            # Buscar la red específica
            network_row = df[df['ESSID'].str.contains('fh_a88c80', na=False)]
            if not network_row.empty:
                power = network_row['Power'].iloc[0]
                # Convertir potencia de dBm a valor positivo para el mapa
                power_value = abs(float(power))
                powers.append(power_value)
                coordinates.append(locations[dump_names[i]])
            else:
                print(f"Red fh_a88c80 no encontrada en {csv_file}")
        except Exception as e:
            print(f"Error al leer {csv_file}: {e}")
    
    if len(powers) < 2:
        print("Se necesitan al menos 2 mediciones para generar el mapa de calor")
        return
    
    # Agregar el AP en el centro con potencia máxima estimada
    coordinates.append(locations['AP'])
    powers.append(max(powers) + 20)  # Estimación de potencia en el AP
    
    # Extraer coordenadas X e Y
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    
    # Crear grid para interpolación
    x_min, x_max = min(x_coords) - 2, max(x_coords) + 2
    y_min, y_max = min(y_coords) - 2, max(y_coords) + 2
    
    xi = np.linspace(x_min, x_max, 100)
    yi = np.linspace(y_min, y_max, 100)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    
    # Interpolación de los datos
    zi = griddata((x_coords, y_coords), powers, (xi_grid, yi_grid), method='cubic')
    
    # Crear el mapa de calor
    plt.figure(figsize=(12, 10))
    heatmap = plt.contourf(xi_grid, yi_grid, zi, levels=20, cmap='YlOrRd')
    plt.colorbar(heatmap, label='Potencia de Señal (dBm)')
    
    # Marcar las posiciones de medición
    for i, (name, coord) in enumerate(locations.items()):
        if name == 'AP':
            plt.plot(coord[0], coord[1], 'ro', markersize=12, label='Access Point')
        elif i-1 < len(powers)-1:  # Verificar si tenemos datos para este punto
            plt.plot(coord[0], coord[1], 'bo', markersize=8)
            plt.annotate(name, (coord[0], coord[1]), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10)
    
    plt.title('Mapa de Calor - Red WiFi fh_a88c80', fontsize=16)
    plt.xlabel('Distancia Este-Oeste (metros)', fontsize=12)
    plt.ylabel('Distancia Norte-Sur (metros)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('heatmap.png', dpi=300)
    print("\nImagen guardada como 'heatmap.png' en la carpeta actual.")
    plt.show()
    
    # Mostrar datos recolectados
    print("\nDatos de potencia recolectados:")
    for i, power in enumerate(powers[:-1]):  # Excluir el AP estimado
        print(f"{dump_names[i]}: {power} dBm en posición {coordinates[i]}")

# Ejecutar la función
if __name__ == "__main__":
    generate_wifi_heatmap()