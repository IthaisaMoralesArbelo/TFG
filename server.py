# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero server.py

#!/usr/bin/env python3
import threading
import socket
import datetime
import hashlib
import time
import sys
import os
from scapy.all import *
import paramiko

from funciones_auxiliares.cuantificacion import cuantificacion
from funciones_auxiliares.reconciliacion import reconciliacion
from funciones_auxiliares.amplificacion import amplificacion

from funciones_auxiliares.sondeo import  iniciarGrafica, media

########### Parámetros de configuración ###########
INTERFACE = "wlan1"  
RSSI_FILE = "rssi_log.txt"
RSSI_FILE_CANAL_A = "rssi_canal_a.txt"
SSID = "RSSI"
mac_cliente = "e4:fa:c4:6f:6f:bf"
mac_servidor = "e4:fa:c4:6f:6f:6a"

####################################################
# Variables globales
client_secuencia = None
secuencia = None
secuencia_reconciliacion = None
last_timestamp = {} #Almacenamos la hora de la última medición para solo tener una máx por segundo y que grafique bien
stop_beacons = False
stop_sniff = False

########## valores para paramiko (sustituo de scp) ##########
CLIENTE_IP = "10.20.52.43"  
CLIENTE_USER = "raspberrypiclient"  
CLIENTE_PASSWORD = "csas1234"  
CLIENTE_RSSI_FILE = "/home/raspberrypiclient/Desktop/prueba/rssi_log.txt"  
CLIENTE_RSSI_FILE_GLOBAL = "/home/raspberrypiclient/Desktop/prueba/rssi_canal_b.txt" 
SERVER_RSSI_FILE_B = "rssi_log_B.txt"
SERVER_RSSI_FILE_B_GLOBAL = "rssi_canal_b.txt"



def obtener_archivo_cliente():
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(CLIENTE_IP, username=CLIENTE_USER, password=CLIENTE_PASSWORD)
    sftp = ssh.open_sftp()
    sftp.get(CLIENTE_RSSI_FILE, SERVER_RSSI_FILE_B)
    sftp.close()
    ssh.close()
  except Exception as e:
    print(f"[SERVER] Error al transferir el archivo: {e}")

def obtener_archivo_global_cliente():
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(CLIENTE_IP, username=CLIENTE_USER, password=CLIENTE_PASSWORD)
    sftp = ssh.open_sftp()
    sftp.get(CLIENTE_RSSI_FILE_GLOBAL, SERVER_RSSI_FILE_B_GLOBAL)
    sftp.close()
    ssh.close()
  except Exception as e:
    print(f"[SERVER] Error al transferir el archivo: {e}")


def enviar_beacons():
  global stop_beacons
  while not stop_beacons:  
    dot11 = Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=mac_servidor, addr3=mac_servidor)
    beacon = Dot11Beacon(cap="ESS+privacy")
    essid = Dot11Elt(ID="SSID", info=SSID, len=len(SSID))
    frame = RadioTap() / dot11 / beacon / essid
    sendp(frame, iface=INTERFACE, count=1, verbose=False)
    print("[SERVER] Beacon enviado")
    time.sleep(0.5)  


def enviar_probe_response(cliente_mac):
  dot11 = Dot11(type=0, subtype=5, addr1=mac_cliente, addr2=mac_servidor, addr3=mac_servidor)
  probe_resp = Dot11ProbeResp()
  essid = Dot11Elt(ID="SSID", info=SSID, len=len(SSID))
  frame = RadioTap() / dot11 / probe_resp / essid
  sendp(frame, iface=INTERFACE, count=1, verbose=False)
  print(f"[SERVER] Enviado Probe Response a {cliente_mac}")



def manejar_probe_request(pkt):
  if stop_sniff:
    return  
  if pkt.haslayer(Dot11) and pkt.type == 0 and pkt.subtype == 4:
    cliente_mac = pkt.addr2
    print(f"[SERVER] Probe Request de {cliente_mac} para {pkt.info.decode(errors='ignore')}")
    enviar_probe_response(cliente_mac)


def packet_handler(pkt, num_paquetes, intervalo):
  global num_paquetes_global
  if num_paquetes_global <= 0:
    return False
  if pkt.haslayer(Dot11):
    if pkt.type == 0 and pkt.subtype in [4, 5, 8]:  
      mac_origen = pkt.addr2
      mac_destino = pkt.addr1
      rssi = None
      try:
        if pkt.haslayer(RadioTap) and hasattr(pkt,"dBm_AntSignal"):
          rssi =pkt.dBm_AntSignal
      except Exception as e:
        rssi = None
        print("Error al extraer RSSI:", e)
            
      if rssi is not None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if mac_origen not in last_timestamp or time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(last_timestamp[mac_origen], "%Y-%m-%d %H:%M:%S")) >= 1:
          entry = f"{timestamp}, {mac_origen} -> {mac_destino}, {rssi} dBm"
          print(entry)
          if (mac_origen == mac_servidor and mac_destino == mac_cliente) or (mac_origen == mac_cliente and mac_destino == mac_servidor):
            with open(RSSI_FILE, "a") as f:
              f.write(entry + "\n")
          else:
            with open(RSSI_FILE_CANAL_A, "a") as f:
              f.write(entry + "\n")
          num_paquetes -= 1
          last_timestamp[mac_origen] = timestamp
          if num_paquetes <= 0:
            return False

def sniff_rssi(num_paquetes, intervalo):
  global num_paquetes_global
  num_paquetes_global = num_paquetes
  tiempo_total = num_paquetes * intervalo + 2
  inicio = time.time()
  def condicion_parada(pkt):
    return stop_sniff or stop_beacons or (time.time() - inicio) > (num_paquetes * intervalo + 2)
  sniff(iface=INTERFACE, prn= lambda pkt: packet_handler(pkt, num_paquetes, intervalo), store=0, stop_filter=condicion_parada)


def exchange_rssi(conn, num_paquetes, intervalo):
  try:
    try:
      os.remove(RSSI_FILE)
      print(f"[SERVER]: Se ha borrado el archivo {RSSI_FILE} resultante del proceso de sondeo del canal anterior.")
    except FileNotFoundError:
      print(f"[SERVER]: Archivo {RSSI_FILE} no encontrado. Se creará uno nuevo.")
    except Exception as e:
      print(f"[SERVER]: Error al borrar {RSSI_FILE}: {e}")
    try:
      os.remove(SERVER_RSSI_FILE_B)
      print(f"[SERVER]: Se ha borrado el archivo {SERVER_RSSI_FILE_B} resultante del proceso de sondeo del canal anterior.")
    except FileNotFoundError:
      print(f"[SERVER]: Archivo {SERVER_RSSI_FILE_B} no encontrado. Se creará uno nuevo.")
    except Exception as e:
      print(f"[SERVER]: Error al borrar {SERVER_RSSI_FILE_B}: {e}")
    try:
      os.remove(RSSI_FILE_CANAL_A)
      print(f"[SERVER]: Se ha borrado el archivo {RSSI_FILE_CANAL_A} resultante del proceso de sondeo del canal anterior.")
    except FileNotFoundError:
      print(f"[SERVER]: Archivo {RSSI_FILE_CANAL_A} no encontrado. Se creará uno nuevo.")
    except Exception as e:
      print(f"[SERVER]: Error al borrar {RSSI_FILE_CANAL_A}: {e}")
    try:
      os.remove(SERVER_RSSI_FILE_B_GLOBAL)
      print(f"[SERVER]: Se ha borrado el archivo {SERVER_RSSI_FILE_B_GLOBAL} resultante del proceso de sondeo del canal anterior.")
    except FileNotFoundError:
      print(f"[SERVER]: Archivo {SERVER_RSSI_FILE_B_GLOBAL} no encontrado. Se creará uno nuevo.")
    except Exception as e:
      print(f"[SERVER]: Error al borrar {SERVER_RSSI_FILE_B_GLOBAL}: {e}")

    # Hilo para enviar beacons
    t_beacons = threading.Thread(target=enviar_beacons, daemon=True)
    t_beacons.start()

    # Hilo para capturar Probe Requests
    t_sniff_probe = threading.Thread(target=lambda: sniff(iface=INTERFACE, prn=manejar_probe_request, store=0), daemon=True)
    t_sniff_probe.start()

    print(f"[*] Iniciando captura en la interfaz {INTERFACE}...")
    sniff_thread = threading.Thread(target=sniff_rssi, args=(num_paquetes, intervalo), daemon=True)
    sniff_thread.start()
    conn.sendall(f"INICIO_CAPTURA".encode())
    for i in range(num_paquetes + 1):
      time.sleep(intervalo)  
      conn.sendall(f"Paquete {i+1}".encode()) 
      data = conn.recv(1024).decode() 
          
    global stop_beacons, stop_sniff
    stop_beacons = True  
    stop_sniff = True 
    sniff_thread.join()
    print("[SERVER]: Captura de paquetes finalizada.")

  except Exception as e:
    conn.sendall(f"ERROR_GENERAL: {e}".encode())
    

def main():
  print("[SERVER]: Esperando que la interfaz gráfica se conecte.")
  # Variables para asegurar que el orden de las etapas sea el correcto
  sondeo_check = False
  cuantificacion_check = False
  reconciliacion_check = False
  amplificacion_check = False
  existe_conexion = False

  #Creo socket para cliente
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(('0.0.0.0', 5000))
  sock.listen(1)
    
  # Creo socket para la interfaz
  sock_interfaz = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_interfaz.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock_interfaz.bind(('localhost',9000))
  sock_interfaz.listen(1)  
  conn_i, addr_i = sock_interfaz.accept()
  print(f"[SERVER]: Conexión aceptada de la interfaz: {addr_i}.")

  while True:
    print("[SERVER]: Esperando a recibir un comando de la interfaz...")    
    respuesta_interfaz = conn_i.recv(4096).decode()
    print(f"[SERVER]: Comando recibido: {respuesta_interfaz}.")
    comando = respuesta_interfaz.split(" ")[0]
        
    if comando == "SONDEO":
      if sondeo_check or cuantificacion_check or reconciliacion_check or amplificacion_check:
        print("[SERVER]: ERROR. Orden de ejecución incorrecto.")
      else:
        num_paquetes = int(respuesta_interfaz.split(" ")[1])
        intervalo = int(respuesta_interfaz.split(" ")[2])
        frame_contenedor = respuesta_interfaz.split(" ")[3]
        print(f"[SERVER]: Comando de sondeo recibido. Número de paquetes: {num_paquetes}, intervalo: {intervalo}, frame: {frame_contenedor}.")
        print("[SERVER]: Esperando a cliente que se conecte para comenzar con la captura de paquetes...")
        conn, addr = sock.accept()
        print(f"[SERVER]: Cliente conectado ({addr}).")
        exchange_rssi(conn, num_paquetes, intervalo)
        sondeo_check = True
        conn.close()
        obtener_archivo_cliente()
        obtener_archivo_global_cliente()
        conn_i.send("INICIAR_GRAFICA".encode())
        print("[SERVER]: Sondeo del canal completado.")
      
      elif comando == "CUANTIFICACION":
        print("[SERVER]: Comando de cuantificación recibido.")
        global secuencia, client_secuencia
        if cuantificacion_check or reconciliacion_check or amplificacion_check:
          print(f"[SERVER]:ERROR. Orden de ejecución incorrecto.")
        elif sondeo_check:
          valor_medio = media(RSSI_FILE)
          print(f"[SERVER]: Valor medio utilizado para la etapa de cuantificacion: {valor_medio}.")
          secuencia = cuantificacion(valor_medio)
          print(f"Secuencia calculada por el SERVER en la cuantificacion: {secuencia}")
          print("[SERVER]: Esperando a cliente que se conecte para enviarle la secuencia generada...")
          conn, addr = sock.accept()
          print(f"[SERVER]: Cliente conectado ({addr})")
          conn.sendall(secuencia.encode())
          print("[SERVER]: envinado secuencia al cliente")
          client_secuencia = conn.recv(1024).decode()
          print(f"[SERVER]: Secuencia recibida por el cliente: {client_secuencia}.")
          conn.close()
          cuantificacion_check = True
          conn_i.send(f"INFO_CUANTIFICACION,{secuencia},{client_secuencia}".encode())
          print("[SERVER]: Cuantificación completada.")
        else:
          print("[SERVER]: ERROR. No se ha realizado el sondeo del canal previamente.")


      elif comando == "RECONCILIACION":
        print("[SERVER]: Comando de reconciliacion recibido.")
        if amplificacion_check or reconciliacion_check:
          print("[SERVER]: ERROR. Orden de ejecución incorrecto. Ya se realizó esta etapa anteriormente.")
        elif cuantificacion_check:
          global secuencia_reconciliacion
          secuencia_reconciliacion = reconciliacion(secuencia, client_secuencia)
          print(f"[SERVER]: Secuencia resultante tras la reconciliacion: {secuencia_reconciliacion}.")
          reconciliacion_check = True
          conn_i.send(f"INFO_RECONCILIACION|{secuencia_reconciliacion}".encode())
        else:
          print("[SERVER]: ERROR. Orden de ejecución incorrecto. Debe realizar primero el sondeo del canal.")

      elif comando == "AMPLIFICACION":
        print("[SERVER]: Comando de amplificación recibido.")
        if amplificacion_check:
          print("[SERVER]: ERROR. Orden de ejecución incorrecto. Esta etapa ya se ha realizado.")
        elif reconciliacion_check != True:
          print("[SERVER]: ERROR. Debe realizar las etapas anteriores en el orden indicado.")
        else:
          clave_compartida = amplificacion(secuencia_reconciliacion)
          amplificacion_check = True
          conn_i.send(f"INFO_AMPLIFICACION,{cuantificacion}".encode())
          print(f"CLAVE COMPARTIDA GENERADA : {clave_compartida}")
 
      elif comando == "CERRAR":
        print("[SERVER]: Cerrando programa")
        sock.close()
        sock_interfaz.close()
        sys.exit(0)
        break;

      else:
        print(f"[SERVER] Comando recibido por la interfaz desconocido: {comando}")
        sock.close()
        sock_interfaz.close()
        sys.exit(1)



if __name__ == "__main__":
    main()
