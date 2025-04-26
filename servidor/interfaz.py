# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero interfaz.py: Contiene la interfaz gráfica del programa. 


import socket
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from funciones_auxiliares.sondeo import iniciarGrafica, iniciarSegundaGrafica, generarEstadisticas
from funciones_auxiliares.cuantificacion import generarInfoCuantificacion
from funciones_auxiliares.reconciliacion import generarInfoReconciliacion
from funciones_auxiliares.amplificacion import generarInfoAmplificacion

import funciones_auxiliares.estadisticasPDF as archivo


########### Variables y parámetros globales ########### 

SERVER_IP = "10.20.50.18"
CLIENT_IP = "10.20.50.17"

# Variables para los sockets
server_socket = None
client_socket = None


########### Funciones ########### 

# Función para conectar los sockets al servidor y al cliente
# y escuchar los mensajes entrantes
def conectar_sockets():
  global server_socket, client_socket
  try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('localhost', 9000))
    print("[INTERFAZ]: Conectada al servidor.")
    hilo_escucha = threading.Thread(target=escuchar_mensajes)
    hilo_escucha.daemon = True
    hilo_escucha.start()
  except ConnectionRefusedError:
    print("[INTERFAZ]: No se pudo conectar al servidor.")
  except Exception as e:
    print(f"[INTERFAZ]: Error al conectar al servidor: {e}")
  try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CLIENT_IP, 8000))
    print("[INTERFAZ]: Conectada al cliente.")
  except ConnectionRefusedError:
    print("[INTERFAZ]: No se pudo conectar al cliente.")
  except Exception as e:
    print(f"[INTERFAZ]: Error al conectar al cliente: {e}")


# Dado el frame que contiene las gráficas, cuadros de texto y demás widgets,
# se eliminan todos los widgets que contiene.
def borrar_pantalla(frame):
  for widget in frame.winfo_children():
    widget.destroy()


# Función para escuchar los mensajes del servidor y del cliente
# y ejecutar las funciones correspondientes
def escuchar_mensajes():
  global server_socket
  while True:
    try:
      mensaje = server_socket.recv(1024).decode('utf-8')
      if mensaje == "INICIAR_GRAFICA":
        app.after(0, iniciarGrafica, columna_derecha)  # Ejecutar en el hilo principal
        app.after(100, generarEstadisticas, columna_derecha, variable_numero_paquetes.get(), variable_tiempo.get())
        
      if mensaje.startswith("INFO_CUANTIFICACION"):
        borrar_pantalla(columna_derecha)
        parametros = mensaje.split(",")
        secuencia= parametros[1]
        secuencia_cliente = parametros[2]
        app.after(0, generarInfoCuantificacion, columna_derecha, secuencia, secuencia_cliente)

      if mensaje.startswith("INFO_RECONCILIACION"):
        parametros = mensaje.split(",")
        secuencia_reconciliada = parametros[1]
        secuencia = parametros[2]
        secuencia_cliente = parametros[3]
        app.after(0, generarInfoReconciliacion, columna_derecha, secuencia_reconciliada, secuencia, secuencia_cliente)

      if mensaje.startswith("INFO_AMPLIFICACION"):
        parametros = mensaje.split(",")
        clave = parametros[1]
        app.after(0, generarInfoAmplificacion, columna_derecha, clave)

    except Exception as e:
      print(f"[INTERFAZ]: Error al recibir mensaje del servidor: {e}")


# Función para cerrar la aplicación y los sockets
def cerrar_aplicacion():
  global server_socket, client_socket
  print("[INTERFAZ]: Cerrando aplicación...")
  if server_socket:
    try:
      server_socket.sendall("CERRAR".encode())
      print("[INTERFAZ]: Servidor desconectado.")
    except Exception as e:
      print(f"[INTERFAZ]: Error al cerrar el servidor: {e}")

  if client_socket:
    try:
      client_socket.sendall("CERRAR".encode())
      client_socket.close()
      print("[INTERFAZ]: Cliente desconectado.")
    except Exception as e:
      print(f"[INTERFAZ]: Error al cerrar el cliente: {e}")

  app.quit()
  app.destroy()
  print("[INTERFAZ]: Aplicación cerrada correctamente.")


# Función para resetear los campos del formulario 
def reseteo_campos():
  variable_numero_paquetes.set("")
  variable_tiempo.set("")


# Función para crear un frame con una barra de desplazamiento
def crear_frame_desplazable(root):
  contenedor = tk.Frame(root, bg="white")
  contenedor.pack(side="right", fill="both", expand=True)

  canvas = tk.Canvas(contenedor, bg="white")
  scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview, bg="white")

  frame_scrollable = tk.Frame(canvas)  

  frame_scrollable.bind(
    "<Configure>", 
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
  )
    
  frame_scrollable.pack(fill="both", expand=True)

  canvas.create_window((0, 0), window=frame_scrollable, anchor="nw")
  canvas.configure(yscrollcommand=scrollbar.set)
  canvas.pack(side="left", fill="both", expand=True)

  scrollbar.pack(side="right", fill="y")
  return frame_scrollable
    
# Función que envía el comando SONDEO junto con sus parámetros al servidor 
# y cliente
def inicio_sondeo(frame):
  numero_paquetes = variable_numero_paquetes.get()
  tiempo_paquetes = variable_tiempo.get()
  if server_socket:
    print("[INTERFAZ]: Enviando comando 'SONDEO' al servidor.")
    server_socket.sendall(f"SONDEO {numero_paquetes} {tiempo_paquetes} {frame}".encode())
  if client_socket:
    print("[INTERFAZ]: Enviando comando 'SONDEO' al cliente.")
    client_socket.sendall(f"SONDEO {numero_paquetes} {tiempo_paquetes}".encode())


# Función para generar la gráfica general del canal
def estadisticas_comunicacion():
   app.after(0, iniciarSegundaGrafica, columna_derecha)


# Función que envía el comando CUANTIFICACION al servidor y cliente
def cuantificacion():
  if server_socket:
    print("[INTERFAZ]: Enviando comando 'CUANTIFICACION' al servidor.")
    server_socket.sendall("CUANTIFICACION".encode())
  if client_socket:
    print("[INTERFAZ]: Enviando comando 'CUANTIFICACION' al cliente.")
    client_socket.sendall("CUANTIFICACION".encode())


# Función que envía el comando RECONCILIACION al servidor y cliente
def reconciliacion():
  if server_socket:
    print("[INTERFAZ]: Enviando comando 'RECONCILIACION' al servidor.")
    server_socket.sendall("RECONCILIACION".encode())
  if client_socket:
    print("[INTERFAZ]: Enviando comando 'RECONCILIACION' al cliente.")
    client_socket.sendall("RECONCILIACION".encode())


# Función que envía el comando AMPLIFICACION al servidor y cliente
def amplificacion():
  if server_socket:
    print("[INTERFAZ]: Enviando comando 'AMPLIFICACION' al servidor.")
    server_socket.sendall("AMPLIFICACION".encode())
  if client_socket:
    print("[INTERFAZ]: Enviando comando 'AMPLIFICACION' al cliente.")
    client_socket.sendall("AMPLIFICACION".encode())

def info_proyecto(): 
  ventana_qr = tk.Toplevel(app) 
  ventana_qr.title("Información del Proyecto") 
  ventana_qr.config(bg="white")
  try: 
    imagen_qr = Image.open("images.png") 
    imagen_qr = imagen_qr.resize((250, 250), Image.LANCZOS) 
    imagen_tk = ImageTk.PhotoImage(imagen_qr)

    etiqueta = tk.Label(ventana_qr, image=imagen_tk, bg="white")
    etiqueta.image = imagen_tk  # Importante para que no se elimine
    etiqueta.pack(pady=20)

    texto = tk.Label(ventana_qr, text="Escanea el código para acceder al PDF del proyecto", bg="white", font=("Arial", 12))
    texto.pack(pady=10)

  except Exception as e: print("Error al cargar el QR:", e)


# Función que genera el archivo que resume todas las métricas del proceso
def generar_archivo():
  if archivo.informacion:
    with open("Proceso_de_Generacion_de_Claves.txt", "w") as f:
      f.write(archivo.informacion)
    print("[INTERFAZ]: Archivo txt generado.")
  else:
    print("[INTERFAZ]: No se ha podido crear el archivo.")
    
    
####### Estructura programa principal #######
app = tk.Tk()
app.config(bg = 'white')
app.minsize(800, 600)
app.title("Generación de claves compartidas en dispositivos IoT a partir de la capa física")
app.geometry("1000x400")
app.font = ("Arial", 14)


####### Encabezado #######
encabezado = tk.Frame(app, bg = 'white', height = 100)
encabezado.pack(fill = "x", side = "top", pady = 10)
titulo_encabezado = tk.Label(encabezado, text = "Generación de claves compartidas en dispositivos IoT a partir de la capa física", font = ("Arial", 20), bg = 'white')
titulo_encabezado.pack(fill = "x", padx = 10, pady = 10)
linea_encabezado = tk.Frame(app, bg = "#5c068c", height = 3)
linea_encabezado.pack(fill = "x", side = "top")


####### Cuerpo #######
cuerpo = tk.Frame(app, bg = 'white')
cuerpo.pack(fill = "both", expand = True)

####### Columna derecha #######
columna_derecha = crear_frame_desplazable(cuerpo)
recuadro = tk.Frame(columna_derecha, bg="white", bd=2, relief="solid", padx=100, pady=100)
recuadro.pack(fill="both", expand=True, padx=20, pady=20, anchor="w")
tk.Label(
    recuadro,
    text="Instrucciones de modo de uso del sistema",
    font=("Arial", 20, "bold")
).pack(pady=10, fill="x")
instrucciones = [
    "1. Rellenar los campos 'Número de paquetes a enviar' y 'Tiempo entre paquetes'.",
    "2. Ir seleccionando de forma ordenada las opciones del menú. En caso de seleccionar las etapas de forma desordenada, estas no se llevarán a cabo.",
    "3. En 'Información del proyecto' encontrará un QR para revisar la documentación.",
    "4. En el caso que desee guardar los datos generados durante la ejecución pulse 'Descargar PDF'."
]
for paso in instrucciones:
    tk.Label(recuadro, text=paso, anchor="w", bg="white", font=("Helvetica", 13)).pack(fill="x", padx=5)


espaciador = tk.Frame(recuadro, height=30, bg="white")
espaciador.pack(fill="x", expand=False)

tabla_etapas = ttk.Treeview(recuadro, columns=("Etapa", "Descripción"), show="headings", height=5)
tabla_etapas.heading("Etapa", text="Etapa")
tabla_etapas.heading("Descripción", text="Descripción")

tabla_etapas.column("Etapa", width=80)
tabla_etapas.column("Descripción")

etapas_info = [
    ("Sondeo cel canal", "Captura de paquetes entre las dos Raspberry's con el objetivo de obtener mediciones de RSSI del canal."),
    ("Cuantificación", "Conversión de los valores analógicos de RSSI en una secuencia binaria."),
    ("Reconciliación", "Proceso de comparación de las secuencias cliente y servidor hasta definir una secuencia común."),
    ("Amplificación de privacidad", "Proceso de amplificación de la secuencia común para aumentar la seguridad.")
]

for etapa, desc in etapas_info:
    tabla_etapas.insert("", "end", values=(etapa, desc))

tabla_etapas.pack(fill="x", expand=False)

espaciador = tk.Frame(recuadro, height=30, bg="white")
espaciador.pack(fill="x", expand=False)

tk.Label(
    recuadro,
    text="Glosario de términos",
    font=("Arial", 20, "bold")
).pack(pady=10, fill="x")

glosario = [
    "* RSSI  -->  Received Signal Strength Indicator. Medida de la intensidad de la señal recibida.",
    "* Entropía  -->  En nuestro caso, grado de aleatoridad de las medidas o de la secuencia generada.",
    "* BDR  -->  Tasa de desacuerdo de bits (Bit disagreement rate).",
    "* Autocorrelación  -->  Mide cómo un valor en la secuencia se relaciona con otro valor desplazado por k posiciones.",
    "* Métrica de Hamming  -->   Cuantifica la diferencia entre dos secuencias binarias del mismo tamaño.",
    "* Hash  -->  Función criptográfica que transofroma una entrada en una salida de longitud fija, irreconocible y única.",
    "* Reciprocidad del canal  -->  Condición del canal. Las características del canal son similares en ambas direcciones .",
    "* Variación temporal  -->  Condición del canal. Las características del canal varían con el tiempo.",
    "* Decorrelación espacial  -->  Condición del canal. Las características del canal varían significativamente con pequeñas variaciones en la posición espacial."
]
for termino in glosario:
    tk.Label(recuadro, text=termino, anchor="w", bg="white", font=("Helvetica", 13)).pack(fill="x", padx=5)
espaciador = tk.Frame(recuadro, height=30, bg="white")
espaciador.pack(fill="x", expand=False)


####### Columna izquierda #######
columna_izquierda = tk.Frame(cuerpo, bg = 'white', width = 500)
columna_izquierda.pack(fill = "y", side = "left", padx = 10, pady = 10)
linea_separadora = tk.Frame(cuerpo, width=3, bg="#5c068c")
linea_separadora.pack(fill="y", side="left", padx=5)


# Número paquetes a enviar
numero_paquetes = tk.Label(columna_izquierda, text = "Número de paquetes a enviar", font = app.font, bg = 'white')
numero_paquetes.pack(fill = "x", pady = 5)
variable_numero_paquetes = tk.StringVar(columna_izquierda)
entrada_numero_paquetes = tk.Entry(columna_izquierda, font = app.font, textvariable = variable_numero_paquetes)
entrada_numero_paquetes.pack(fill = "x", pady = 5)


# Tiempo entre paquetes
variable_tiempo = tk.StringVar(columna_izquierda)
tiempo_entre_paquetes = tk.Label(columna_izquierda, text = "Tiempo entre paquetes (s)", font = app.font, bg = 'white')
tiempo_entre_paquetes.pack(fill = "x", pady = 5)
entrada_tiempo = tk.Entry(columna_izquierda, font = app.font, textvariable = variable_tiempo)
entrada_tiempo.pack(fill = "x", pady = 5)


# Botón reseto de campos
boton_reseteo = tk.Button(columna_izquierda, text = "Resetear valores", font = app.font, bg = "#5c068c", fg = "white", command = reseteo_campos).pack(fill = "x", pady = 5)

####### Columna izquierda parte inferior #######
barra_separadora = tk.Frame(columna_izquierda, bg = "#5c068c", height = 3).pack(fill = "x", pady = 15)
boton_uno = tk.Button(columna_izquierda, text = "Sondeo del Canal", font = app.font, bg = "#5c068c", command= lambda: inicio_sondeo(columna_derecha), fg = "white").pack(fill = "x", pady = 5)
boton_dos = tk.Button(columna_izquierda, text = "Imagen general del canal", font = app.font, bg = "#5c068c", command = lambda:estadisticas_comunicacion(), fg = "white").pack(fill = "x", pady = 5)
boton_tres = tk.Button(columna_izquierda, text = "Cuantificación", font = app.font, bg = "#5c068c", command = cuantificacion, fg = "white").pack(fill = "x", pady = 5)
boton_cuatro = tk.Button(columna_izquierda, text = "Reconciliación", font = app.font, bg = "#5c068c", command = reconciliacion, fg = "white").pack(fill = "x", pady = 5)
boton_cinco = tk.Button(columna_izquierda, text = "Amplificación de privacidad", font = app.font, command = amplificacion, bg = "#5c068c", fg = "white").pack(fill = "x", pady = 5)
boton_seis = tk.Button(columna_izquierda, text = "Información sobre el proyecto", command= info_proyecto, font = app.font, bg = "#5c068c", fg = "white").pack(fill = "x", pady = 5)
boton_siete = tk.Button(columna_izquierda, text = "Descargar PDF", font = app.font, command= generar_archivo, bg = "#5c068c", fg="white").pack(fill = "x", pady = 5)
barra_separadora = tk.Frame(columna_izquierda, bg = "#5c068c", height = 3).pack(fill = "x", pady = 15)


####### Footer #######
footer = tk.Frame(app, bg="#5c068c")
footer.pack(fill="x", side="bottom")
try:
  imagen = Image.open("images.png")  
  imagen = imagen.resize((40, 40), Image.LANCZOS)
  logo = ImageTk.PhotoImage(imagen)
  label_logo = tk.Label(footer, image=logo, bg="#5c068c")
  label_logo.pack(pady=5)
except Exception as e:
    print("Error cargando el logo:", e)
texto_footer = tk.Label(footer, 
                        text="Ithaisa Morales Arbelo. Universidad de La Laguna", 
                        bg="#5c068c", 
                        fg="white",
                        font=("Arial", 13))
texto_footer.pack(padx=5, pady=10)

conexion_thread = threading.Thread(target=conectar_sockets)
conexion_thread.start()

app.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

app.mainloop()
