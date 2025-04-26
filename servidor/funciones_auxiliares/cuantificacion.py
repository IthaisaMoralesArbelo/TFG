# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero cuantificacion.py: Contiene las funciones auxiliares relativas al proceso de 
# cuantificación de RSSI y sus métricas.

from collections import Counter
import math
import numpy as np
import os
import re
import tkinter as tk


########### Variables y parámetros globales ########### 

RSSI_FILE= "rssi_log.txt"

########### Métricas ########### 

# Media no adaptativa de RSSI
def media(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    return sum(rssi) / len(rssi)
  return 0


# Dados la media y los valores RSSI, calcula la desviación típica
def desviacionTipica(media, rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append((int(match.group(2)) - media) ** 2)
    return (sum(rssi) / len(rssi)) ** 0.5
  return 0


# Tasa de desacuerdo de bits (BDR, Bit Disagreement Rate)
# Devuelve el porcentaje de bits que no coinciden entre las dos secuencias
def tasaDesacuerdo(secuencia_server, secuencia_client):
  assert(len(secuencia_server) == len(secuencia_client)), "Las secuencias generadas tienen longitudes diferentes"
  diferencias = 0
  for a,b in zip(secuencia_server, secuencia_client):
    if a != b:
      diferencias += 1
  return diferencias / len(secuencia_server)


# Calcula la autocorrelación de una secuencia de bits
def autocorrelacion(secuencia):
  secuencia = [int(x) for x in secuencia]
  k = 1
  n = len(secuencia)
  if k >= n:
    return 0
  suma = 0
  for i in range(n-k):
    suma += secuencia[i]*secuencia[i+k]
  media = sum(secuencia) / n
  varianza = sum((i - media) ** 2 for i in secuencia) / n
  if varianza == 0:
    return 0
  else :
    return (suma / (n-k)-media**2)/varianza
    

# Calcula la entropía de una secuencia de bits
def entropia(secuencia):
  conteo = Counter(secuencia)
  total=len(secuencia)
  prob = [freq/total for freq in conteo.values()]
  resultado = -sum(p*np.log2(p) for p in prob)
  return resultado
  

# Calcula el valor mínimo y máximo de RSSI
def valorMinimoMaximoRssi(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    return min(rssi), max(rssi)
  else:
    print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
    return None, None


# Devuelve el recuadro de estadísticas de la cuantificación
def generarInfoCuantificacion(frame,secuencia_server, secuencia_client):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la cuantificación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Secuencia de bits de A", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_server, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de bits de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_client, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Tasa de desacuerdo de bits (BDR, Bit Disagreement Rate)", font=("Arial",18,"bold")).pack(pady=10)
  bdr = tasaDesacuerdo(secuencia_server, secuencia_client)
  tk.Label(recuadro, text=bdr, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Autocorrelación de la secuencia", font=("Arial",18,"bold")).pack(pady=10)
  autocorrelacion_a = autocorrelacion(secuencia_server)
  autocorrelacion_b = autocorrelacion(secuencia_client)
  tk.Label(recuadro, text="Autocorrelación de la secuencia de A ", bg="white").pack(pady=5)
  tk.Label(recuadro, text=autocorrelacion_a, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Autocorrelación de la secuencia de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=autocorrelacion_b, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Entropía de la secuencia", font=("Arial",18,"bold")).pack(pady=10)
  entropia_a = entropia(secuencia_server)
  entropia_b = entropia(secuencia_client)
  tk.Label(recuadro, text="Entropía de la secuencia de A ", bg="white").pack(pady=5)
  tk.Label(recuadro, text=entropia_a, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Entropía de la secuencia de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=entropia_b, bg="white").pack(pady=5)


###### Algoritmo de Mathur ######
def cuantificacion(media, desviacion_tipica, valor,rssi_file):
  secuencia = []
  contador = 0
  rangoSuperior = media - 1 * desviacion_tipica
  rangoInferior = media + 1 * desviacion_tipica
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          timestamp = match.group(1)
          rssi = int(match.group(2))
          contador += 1
        if contador > valor: 
          break
        else :
          if rssi > rangoSuperior:
            secuencia.append('1')
          elif rssi < rangoInferior:
            secuencia.append('0')
  secuencia = ''.join(secuencia)
  return secuencia


###### Cuantificación de RSSI utilizando la desviación típica ######
def cuantificacion_dos(rssi_file,desviacion_tipica):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    secuencia = []
    for i in range(1, 10):
      if (rssi[i] - rssi[i-1])<= desviacion_tipica:
        secuencia.append('0')
      else:
        secuencia.append('1')
    secuencia = ''.join(secuencia)
    return secuencia
  return 0


###### Cuantificación de LoRa-Lisk ######
def cuantificacion_tres(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
        
      # Contar la frecuencia de cada valor de RSSI
      total_medidas = len(rssi)
      frecuencia = Counter(rssi)
      probabilidades = {valor: count / total_medidas for valor, count in frecuencia.items()}
        
      # Calcular la entropía del canal
      entropia = -sum(prob * math.log2(prob) for prob in probabilidades.values())
      entropia_entera = int(entropia)
        
      # Calcular el número de niveles
      n_niveles = 2 ** entropia_entera
      n_niveles = max(n_niveles, 2)
      bits_por_nivel = math.log2(n_niveles)
        
      # Determinar los niveles de cuantificación
      rssi_min, rssi_max = min(rssi), max(rssi)
      niveles = np.linspace(rssi_min,rssi_max,total_medidas)
        
      # Asignar códigos binarios a los niveles
      codigos = {niveles[i]: format(i, f'0{int(total_medidas)}b') for i in range(total_medidas)}
        
      # Generar la secuencia final codificada
      secuencia_codificada = "".join(codigos[min(niveles, key=lambda x: abs(x - valor))] for valor in rssi)
    
      return secuencia_codificada

  
# Función que crea una lista de secuencias. Son 2^num_bits posibilidades
def gray(num_bits):
  codigos = []
  for i in range(2 ** num_bits):
    codigos.append(i ^ (i >> 1))
  return codigos


# Función variable
def e(k):
  return 1 if (k % 3 == 1 or k % 5 == 3) else 0
  

###### Esquema de cuantificación multibit adaptativo ######
def cuantificacion_cuatro(rssi, num_bits_secuencia = 16, y_min = -280, y_max = -180):
  y_min, y_max = valorMinimoMaximoRssi(RSSI_FILE)
  k = 4 * (2 ** num_bits_secuencia) 
  umbrales = np.linspace(y_min, y_max, k - 1) # K - 1 umbrales, y_min y y_max son los min y max esperados en un RSSI
  umbrales = [-np.inf] + list(umbrales) + [np.inf]
  nivel_rssi = 0
  while nivel_rssi < k and rssi > umbrales[nivel_rssi]:
    nivel_rssi += 1
  # Genero los códigos de Gray
  codigos = gray(num_bits_secuencia)
  nivel_rssi = (nivel_rssi * 7) % (2 ** num_bits_secuencia)
  # Calculo e(k) para saber si es 1 o 0
  e_k = e(nivel_rssi)
  if e_k == 1:
    nivel_rssi = min(nivel_rssi, len(codigos) - 1)
    resultado = codigos[nivel_rssi]
  else:
    # Gray desplazado
    resultado = codigos[(nivel_rssi + 1) % len(codigos)]  
  secuencia = format(resultado, f'0{num_bits_secuencia}b') 
  return secuencia
