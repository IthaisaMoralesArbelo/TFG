# # Universidad de La Laguna
# # Escuela Superior de Ingeniería y Tecnología
# # Grado en Ingeniería Informática
# # Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# # Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# # Fecha: 13/02/2025
# # Fichero funciones_auxiliares.py del servidor

# import os
# import re
# import hashlib
# import numpy as np
# import tkinter as tk
# import matplotlib
# matplotlib.use("TkAgg")
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from collections import Counter
# import math

# #Variables globales
# RSSI_FILE_A = "rssi_log.txt"
# RSSI_FILE_B = "rssi_log_B.txt"
# RSSI_FILE_CANAL_A = "rssi_canal_a.txt"  
# RSSI_FILE_CANAL_B = "rssi_canal_b.txt"  

# media_rssi_a = 0
# media_rssi_n = 0

# rssi_a_total = []
# rssi_b_total = []

# timestamps = []
# rssi_values_a = []
# rssi_values_b = []
# rssi_a = {}
# rssi_b = {}
# rssi_canal_a = {}
# rssi_canal_b = {}


# #Función para graficar únicamente la primera medición por segundo
# def filtrar_mediciones_unicas(lineas):
#     timestamps_revisadas = set()
#     filtradas = []
#     for linea in lineas:
#         match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), (\S+) -> (\S+), (-\d+)\s+dBm", linea)
#         if match:
#             timestamp = match.group(1)
#             if timestamp not in timestamps_revisadas:
#                 timestamps_revisadas.add(timestamp)
#                 filtradas.append(linea)
#     return filtradas


# def iniciar_grafica(frame_contenedor):
#     global figure, ax, canvas, toolbar, anim
#     global timestamps, rssi_values_a, rssi_values_b

#     # Limpiar contenedor
#     for widget in frame_contenedor.winfo_children():
#         widget.destroy()

#     timestamps.clear()
#     rssi_values_a.clear()
#     rssi_values_b.clear()

#     figure, ax = plt.subplots(figsize=(6, 4))
#     ax.set_title("Sondeo del canal")
#     ax.set_xlabel("Tiempo")
#     ax.set_ylabel("RSSI (dBm)")
#     ax.set_ylim(-40, 0)

#     canvas = FigureCanvasTkAgg(figure, master=frame_contenedor)
#     canvas.get_tk_widget().pack(fill="both", expand=True)

#     toolbar = NavigationToolbar2Tk(canvas, frame_contenedor)
#     toolbar.update()
#     toolbar.pack(side="top", fill="x")

#     anim = FuncAnimation(figure, actualizar_grafica, interval=1000, save_count=100)


# def actualizar_grafica(frame):
#     global ax, canvas, timestamps
#     global media_rssi_a, media_rssi_b
#     if os.path.exists(RSSI_FILE_A):
#         with open(RSSI_FILE_A, "r") as f:
#             for line in f:
#                 match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
#                 if match:
#                     timestamp = match.group(1)
#                     rssi = int(match.group(2))
#                     if timestamp not in rssi_a:
#                         rssi_a[timestamp] = []
#                     rssi_a[timestamp].append(rssi)

# # Leer el archivo de B
#     if os.path.exists(RSSI_FILE_B):
#         with open(RSSI_FILE_B, "r") as f:
#             for line in f:
#                 match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
#                 if match:
#                     timestamp = match.group(1)
#                     rssi = int(match.group(2))
#                     if timestamp not in rssi_b:
#                         rssi_b[timestamp] = []
#                     rssi_b[timestamp].append(rssi)

# # Calcular la media de RSSI por segundo
#     timestamps = sorted(set(rssi_a.keys()) & set(rssi_b.keys()))  # Solo timestamps en ambos archivos
#     valores_a = [sum(rssi_a[t]) / len(rssi_a[t]) for t in timestamps]
#     valores_b = [sum(rssi_b[t]) / len(rssi_b[t]) for t in timestamps]
#     media_rssi_a = media(RSSI_FILE_A)
#     media_rssi_b = media(RSSI_FILE_B)
#     ax.clear()
#     ax.set_title("Sondeo del canal")
#     ax.set_xlabel("Tiempo")
#     ax.set_ylabel("RSSI (dBm)")
#     ax.set_ylim(-40, 0)

#     ax.plot(timestamps, valores_a, 'o-', color='purple', label="RSSI A")
#     ax.plot(timestamps, valores_b, 's-', color='orange', label="RSSI B")
#     ax.axhline(media_rssi_a, color='purple', linestyle='dashed', label="RSSI A (media)")
#     ax.axhline(media_rssi_b, color='orange', linestyle='dashed', label="RSSI B (media)")
#     ax.legend()

#     canvas.draw()





# def filtrado_ruido(conjunto_mediciones, diferencia = 10):
#   if not conjunto_mediciones:
#     return 0
#   media_sin_filtrar = sum(conjunto_mediciones) / len(conjunto_mediciones)
#   mediciones_filtradas = []
#   for i in range(len(conjunto_mediciones)):
#     if i == 0:
#       mediciones_filtradas.append(conjunto_mediciones[i])
#     else:
#       if abs(conjunto_mediciones[i] - media_sin_filtrar) < diferencia:
#         mediciones_filtradas.append(conjunto_mediciones[i])
#       else:
#         mediciones_filtradas.append(media_sin_filtrar)

#   valor_medio_rssi = sum(mediciones_filtradas) / len(mediciones_filtradas)
#   return valor_medio_rssi


# def generar_estadisticas(frame, numero_paquetes, tiempo_entre_paquetes):
#   global media_rssi_a, media_rssi_b
#   recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
#   recuadro.pack(fill="both", expand=True, padx=20, pady=20)
#   label = tk.Label(recuadro, text="Estadísticas de la comunicación", font=("Arial",18,"bold"))
#   label.pack(pady=10)
#   tk.Label(recuadro, text=f"Número de paquetes enviados: {numero_paquetes}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"Tiempo entre paquetes: {tiempo_entre_paquetes} ms",bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Medias simples de RSSI", bg="white").pack(pady=10)
#   tk.Label(recuadro, text=f"RSSI A: Media={media_no_adaptativa(RSSI_FILE_A):.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"RSSI B: Media={media_no_adaptativa(RSSI_FILE_B):.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Valores RSSI medios tras hacer un filtrado de ruido", bg="white").pack(pady=10)
#   tk.Label(recuadro, text=f"RSSI A: Media={media_rssi_a:.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"RSSI B: Media={media_rssi_b:.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Entropía del canal", bg="white").pack(pady=10)
#   tk.Label(recuadro, text=f"Entropía medida por A: {entropia(RSSI_FILE_A):.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"Entropía medida por B: {entropia(RSSI_FILE_B):.2f}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Valores mínimo y máximo de RSSI del canal entre A y B", bg="white").pack(pady=10)
#   min_a, max_a = valorMinimoMaximoRssi(RSSI_FILE_A)
#   min_b, max_b = valorMinimoMaximoRssi(RSSI_FILE_B)
#   tk.Label(recuadro, text=f"RSSI A: Valor máximo={min_a}, mínimo={max_a}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"RSSI B: Valor máximo={min_b}, mínimo={max_b}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Valores mínimo y máximo de RSSI en el canal de entre todos los dispositivos", bg="white").pack(pady=10)
#   min_canal_a, max_canal_a = valorMinimoMaximoRssi(RSSI_FILE_CANAL_A)
#   min_canal_b, max_canal_b = valorMinimoMaximoRssi(RSSI_FILE_CANAL_B)
#   tk.Label(recuadro, text=f"RSSI A: Valor máximo={min_canal_a}, mínimo={max_canal_a}", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=f"RSSI B: Valor máximo={min_canal_b}, mínimo={max_canal_b}", bg="white").pack(pady=5)



# def generar_info_cuantificacion(frame,secuencia_server, secuencia_client):
#   recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
#   recuadro.pack(fill="both", expand=True, padx=20, pady=20)
#   tk.Label(recuadro, text="Información de la cuantificación", font=("Arial",18,"bold")).pack(pady=10)
#   tk.Label(recuadro, text="Secuencia de bits de A", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=secuencia_server, bg="white").pack(pady=5)
#   tk.Label(recuadro, text="Secuencia de bits de B", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=secuencia_client, bg="white").pack(pady=5)

# def generar_info_reconciliacion(frame, secuencia_reconciliada):
#   recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
#   recuadro.pack(fill="both", expand=True, padx=20, pady=20)
#   tk.Label(recuadro, text="Información de la reconciliación", font=("Arial",18,"bold")).pack(pady=10)
#   tk.Label(recuadro, text="Secuencia de bits reconciliada", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=secuencia_reconciliada, bg="white").pack(pady=5)

# def generar_info_amplificacion(frame, clave_compartida):
#   recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
#   recuadro.pack(fill="both", expand=True, padx=20, pady=20)
#   tk.Label(recuadro, text="Información de la amplificación", font=("Arial",18,"bold")).pack(pady=10)
#   tk.Label(recuadro, text="Clave compartida generada", bg="white").pack(pady=5)
#   tk.Label(recuadro, text=clave_compartida, bg="white").pack(pady=5)
  
# # Función que crea una lista de secuencias. Son 2^num_bits posibilidades
# def gray(num_bits):
#   codigos = []
#   for i in range(2 ** num_bits):
#     codigos.append(i ^ (i >> 1))
#   return codigos


# # Función variable
# def e(k):
#   return 1 if k % 4 == 2 else 0

# def cuantificacion_():
#     media_rssi = media(RSSI_FILE_A)  # Media global de RSSI
#     secuencia_bits = []

#     # Abrir fichero y contar las líneas
#     with open(RSSI_FILE_A, "r") as f:
#         lineas = f.readlines()
#         num_lineas = len(lineas)
#         num_bits_secuencia = 8
#         num_lineas_conjunto = num_lineas // num_bits_secuencia
        
#         # Si el número de líneas no es divisible entre 8, replicar las últimas mediciones
#         if num_lineas % num_bits_secuencia != 0:
#             print(f"El número de líneas no es divisible entre 8, replicando las últimas mediciones.")
#             num_lineas_conjunto += 1  # Añadimos una línea más para distribuir
#             extra_lineas = num_bits_secuencia * num_lineas_conjunto - num_lineas
#             # Añadimos las últimas líneas repetidas si faltan
#             lineas += lineas[-extra_lineas:]

#         # Dividir las mediciones en 8 conjuntos y calcular la media de cada conjunto
#         for i in range(num_bits_secuencia):
#             rssi_total = 0
#             for j in range(num_lineas_conjunto):
#                 match = re.search(r", (-?\d+)\s+dBm", lineas[i * num_lineas_conjunto + j])
#                 if match:
#                     rssi_total += int(match.group(1))
#             media_conjunto = rssi_total / num_lineas_conjunto
#             secuencia_bits.append(media_conjunto)

#     print(f"Conjunto de medias: {secuencia_bits}")

#     # Comparar cada media con la media global
#     for i in range(num_bits_secuencia):
#         if secuencia_bits[i] > media_rssi:
#             secuencia_bits[i] = 1  # Si la media es mayor que la global, se asigna 1
#         else:
#             secuencia_bits[i] = 0  # Si la media es menor o igual, se asigna 0

#     print(f"Secuencia de bits: {secuencia_bits}")
#     return secuencia_bits


# # Paso 2: Cuantificación de la RSSI
# # Multinivel para tener una secuencia de bits
# # Utilizamos MAQ del [1030]
# # Divido en K niveles (igual de probables) k = 4* 2^num_bits_secuencia
# # Adapto los niveles porque si fuesen fijos, si el valor es muy cercano al umbral, hay más prob de q difieran
# # Según eso, el num_bits_secuencia lo decide A y se lo comunica a B quien le sigue, 
# # no sé si es mejor por defecto ambos el mismo
# # no hay censura en este esquema
# # otra opción es con la media que va cambiando a medida q hago las 10 mediciones?
# def cuantificacion(rssi, num_bits_secuencia = 8, y_min = -280, y_max = -180):
#   k = 4 * (2 ** num_bits_secuencia) # niveles igualmente probables
#   # Uso de la función de distribución acumulativa (CDF):inversa de la CDF para calcular los umbrales que separan los niveles(conocer los intervalos)
#   # yo estos valores no los conozco, la idea es hacer intervalos igual de probables
#   # una opción es con la desviación normal estándar
#   #umbrales = [norm.ppf(i / k) for i in range(1, k)] 
#   # y la otra es dividirlos de forma uniforme, pero claro solo tengo un valor entonces min y max definidos por mi?
#   umbrales = np.linspace(y_min, y_max, k - 1) # K - 1 umbrales, y_min y y_max son los min y max esperados en un RSSI
#   umbrales = [-np.inf] + list(umbrales) + [np.inf]
#   #umbrales = [-np.inf] + umbrales + [np.inf] # añado infinitos para los extremos
#   #print(umbrales)
#   nivel_rssi = 0
#   while nivel_rssi < k and rssi > umbrales[nivel_rssi]:
#     nivel_rssi += 1
#   # Genero los códigos de Gray
#   codigos = gray(num_bits_secuencia)
#   # Calculo e(k) para saber si es 1 o 0
#   e_k = e(nivel_rssi)
#   if e_k == 1:
#     nivel_rssi = min(nivel_rssi, len(codigos) - 1)
#     resultado = codigos[nivel_rssi]
#   else:
#     # Gray desplazado
#     resultado = codigos[(nivel_rssi + 1) % len(codigos)]  
#   secuencia = format(resultado, f'0{num_bits_secuencia}b') 
#   return secuencia

# def media(rssi_file, diferencia = 10):
#     if not os.path.exists(rssi_file):
#         print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
#         return None

#     mediciones = []

#     # Leer el archivo y extraer los valores de RSSI
#     with open(rssi_file, "r") as f:
#         for line in f:
#             match = re.search(r", (-?\d+)\s+dBm", line)
#             if match:
#                 mediciones.append(int(match.group(1)))

#     if not mediciones:
#         print(f"[SERVER]: ERROR. No se encontraron mediciones en {rssi_file}")
#         return None

#     media_sin_filtrar = sum(mediciones) / len(mediciones)
#     mediciones_filtradas = []

#     for i in range(len(mediciones)):
#         if i == 0:
#             mediciones_filtradas.append(mediciones[i])
#         else:
#             if abs(mediciones[i] - media_sin_filtrar) < diferencia:
#                 mediciones_filtradas.append(mediciones[i])
#             else:
#                 mediciones_filtradas.append(media_sin_filtrar)

#     valor_medio_rssi = sum(mediciones_filtradas) / len(mediciones_filtradas)
#     return valor_medio_rssi

# # Función que calcula la paridad, devuelve cero si el número de 1 es par.
# def calcularParidad(bits):
#   return sum(bits) % 2 

# # Paso 3: Reconciliación.
# def reconciliacion(mi_secuencia, su_secuencia):
#   secuencia = []
#   for i in range(len(mi_secuencia)):
#     if mi_secuencia[i] == su_secuencia[i]:
#       secuencia.append(mi_secuencia[i])
#     else:
#       secuencia.append('0')
#   paridadA = calcularParidad([int(bit) for bit in mi_secuencia])
#   paridadB = calcularParidad([int(bit) for bit in su_secuencia])
#   if paridadA != paridadB:
#       print("[SERVER]: ERROR. Ha habido un error en la reconciliación.")
#   return secuencia

# def amplificacion(secuencia_bits):
#   secuencia_bits = ''.join(secuencia_bits)
#   print(f"{secuencia_bits}")
#   clave_compartida = hashlib.sha256(secuencia_bits.encode()).digest()
#   return clave_compartida


# def entropia(rssi_file):
#   if os.path.exists(rssi_file):
#     with open(rssi_file, "r") as f:
#       rssi = []
#       for line in f:
#         match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
#         if match:
#           rssi.append(int(match.group(2)))
        
#     # Contamos la frecuencia de cada valor de RSSI
#     total_medidas = len(rssi)
#     frecuencia = Counter(rssi)
#     probabilidades = {valor: count / total_medidas for valor, count in frecuencia.items()}
        
#     # Calcular la entropía del canal
#     entropia = -sum(prob * math.log2(prob) for prob in probabilidades.values())
#     return entropia
#   else:    
#     print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
#     return None


# def valorMinimoMaximoRssi(rssi_file):
#   if os.path.exists(rssi_file):
#     with open(rssi_file, "r") as f:
#       rssi = []
#       for line in f:
#         match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
#         if match:
#           rssi.append(int(match.group(2)))
#     return min(rssi), max(rssi)
#   else:
#     print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
#     return None, None



# def media_no_adaptativa(filename):
#   valores = []
#   if os.path.exists(filename):
#     with open(filename, "r") as f:
#       for line in f:
#         match = re.search(r"(-\d+)\s+dBm", line)
#         if match:
#           valores.append(int(match.group(1)))
#   return sum(valores) / len(valores) if valores else 0

# def iniciar_segunda_grafica(frame_contenedor):
#     global figure, ax, canvas, toolbar, anim, rssi_a, rssi_b, timestamps
#     rssi_a.clear()
#     rssi_b.clear()
#     rssi_canal_a.clear()
#     rssi_canal_b.clear()

#     # Limpiar contenedor
#     for widget in frame_contenedor.winfo_children():
#         widget.destroy()
    
#     figure, ax = plt.subplots(figsize=(6, 4))
#     ax.set_title("Sondeo del canal")
#     ax.set_xlabel("Tiempo")
#     ax.set_ylabel("RSSI (dBm)")
#     ax.set_ylim(-120, 0)

#     canvas = FigureCanvasTkAgg(figure, master=frame_contenedor)
#     canvas.get_tk_widget().pack(fill="both", expand=True)

#     toolbar = NavigationToolbar2Tk(canvas, frame_contenedor)
#     toolbar.update()
#     toolbar.pack(side="top", fill="x")

#     anim = FuncAnimation(figure, actualizar_segunda_grafica, interval=1000, save_count=100)

# def actualizar_segunda_grafica(frame):
#     global figure, ax, canvas, toolbar, anim, rssi_a, rssi_b, timestamps

#     # Limpiar diccionarios de datos
#     rssi_a.clear()
#     rssi_b.clear()
#     rssi_canal_a.clear()
#     rssi_canal_b.clear()

#     def leer_archivo(filename, diccionario):
#         """ Función para leer un archivo de RSSI y almacenar datos en un diccionario """
#         if os.path.exists(filename):
#             with open(filename, "r") as f:
#                 for line in f:
#                     match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
#                     if match:
#                         timestamp = match.group(1)
#                         rssi = int(match.group(2))
#                         if timestamp not in diccionario:
#                             diccionario[timestamp] = []
#                         diccionario[timestamp].append(rssi)

#     # Leer datos de los cuatro archivos
#     leer_archivo(RSSI_FILE_A, rssi_a)
#     leer_archivo(RSSI_FILE_B, rssi_b)
#     leer_archivo(RSSI_FILE_CANAL_A, rssi_canal_a)
#     leer_archivo(RSSI_FILE_CANAL_B, rssi_canal_b)

#     # Obtener timestamps comunes
#     timestamps = sorted(set(rssi_a.keys()) | set(rssi_b.keys()) | set(rssi_canal_a.keys()) | set(rssi_canal_b.keys()))

#     # Calcular valores medios
#     valores_a = [sum(rssi_a[t]) / len(rssi_a[t]) if t in rssi_a else None for t in timestamps]
#     valores_b = [sum(rssi_b[t]) / len(rssi_b[t]) if t in rssi_b else None for t in timestamps]
#     valores_canal_a = [sum(rssi_canal_a[t]) / len(rssi_canal_a[t]) if t in rssi_canal_a else None for t in timestamps]
#     valores_canal_b = [sum(rssi_canal_b[t]) / len(rssi_canal_b[t]) if t in rssi_canal_b else None for t in timestamps]


#     media_rssi_a = media_no_adaptativa(RSSI_FILE_A)
#     media_rssi_b = media_no_adaptativa(RSSI_FILE_B)
#     media_rssi_canal_a = media_no_adaptativa(RSSI_FILE_CANAL_A)
#     media_rssi_canal_b = media_no_adaptativa(RSSI_FILE_CANAL_B)
#     # Limpiar gráfico
#     ax.clear()
#     ax.set_title("Sondeo del canal")
#     ax.set_xlabel("Tiempo")
#     ax.set_ylabel("RSSI (dBm)")
#     ax.set_ylim(-120, 0)

#     # Graficar dispositivos A y B con colores distintivos
#     ax.plot(timestamps, valores_a, 'o-', color='purple', label="RSSI A")
#     ax.plot(timestamps, valores_b, 's-', color='orange', label="RSSI B")

#     # Graficar todos los dispositivos en gris
#     ax.plot(timestamps, valores_canal_a, 'x-', color='gray', alpha=0.3, label="Todos desde A")
#     ax.plot(timestamps, valores_canal_b, 'd-', color='darkgray', alpha=0.3, label="Todos desde B")

#     # Líneas de media
#     ax.axhline(media_rssi_a, color='purple', linestyle='dashed', label="RSSI A (media)")
#     ax.axhline(media_rssi_b, color='orange', linestyle='dashed', label="RSSI B (media)")
#     ax.axhline(media_rssi_canal_a, color='gray', linestyle='dashed', label="Todos desde A (media)")
#     ax.axhline(media_rssi_canal_b, color='darkgray', linestyle='dashed', label="Todos desde B (media)")

#     ax.legend()
#     canvas.draw()
