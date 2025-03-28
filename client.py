# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero client.py

#!/usr/bin/env python3
import threading
import socket
import datetime
import time
import sys
import os
import hashlib
from scapy.all import *
import paramiko

from funciones_auxiliares.cuantificacion import cuantificacion, desviacionTipica, cuantificacion_cuatro
from funciones_auxiliares.reconciliacion import reconciliacion
from funciones_auxiliares.amplificacion import amplificacion
from funciones_auxiliares.sondeo import media

# Parámetros de configuración
INTERFACE = "wlxe4fac46f6fbf"    
RSSI_FILE = "rssi_log.txt"
RSSI_FILE_CANAL_B = "rssi_canal_b.txt"
IP_SERVER = "10.20.52.154" 
mac_cliente = "e4:fa:c4:6f:6f:bf"
mac_servidor = "e4:fa:c4:6f:6f:6a"

secuencia = None
server_secuencia = None
secuencia_reconciliacion = None
existe_conexion = False
stop_beacons = False


last_timestamp = {} 

num_paquetes_global = 0 



def enviar_probe_request(mac_ap, ssid):
  if stop_beacons:
    return
  dot11 = Dot11(type=0, subtype=4, addr1=mac_servidor, addr2=mac_cliente, addr3=mac_servidor)  
  probe_req = Dot11ProbeReq()
  essid = Dot11Elt(ID="SSID", info=ssid.encode(), len=len(ssid))
  frame = RadioTap() / dot11 / probe_req / essid
  sendp(frame, iface=INTERFACE, count=1, verbose=False)
  print(f"[CLIENT] Enviado Probe Request para SSID: {ssid} a {mac_ap}")


def escuchar_beacons():
  if stop_beacons:
    return
  sniff(iface=INTERFACE, prn=lambda pkt: detectar_beacon(pkt), stop_filter=stop_beacons)

def detectar_beacon(pkt):
  if stop_beacons:
    return
  if pkt.haslayer(Dot11Beacon):  
    ssid = pkt[Dot11Elt].info.decode(errors='ignore')  
    print(f"[CLIENT] Beacon recibido con SSID: {ssid}")
    enviar_probe_request(pkt.addr2, ssid)  

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
            with open(RSSI_FILE_CANAL_B, "a") as f:
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
    return stop_beacons or (time.time() - inicio) > tiempo_total 
  sniff(iface=INTERFACE, prn= lambda pkt:  packet_handler(pkt, num_paquetes, intervalo), store=0,stop_filter=condicion_parada )


def exchange_rssi(sock, num_paquetes, intervalo): 
  global stop_beacons
  try:
    try:
      os.remove(RSSI_FILE)
      print(f"[CLIENT]: Se ha borrado el archivo {RSSI_FILE} resultante del proceso de sondeo del canal anterior.")
    except FileNotFoundError:
      print(f"[CLIENT]: Archivo {RSSI_FILE} no encontrado. Se creará uno nuevo.")
    except Exception as e:
      print(f"[CLIENT]: Error al borrar {RSSI_FILE}: {e}")

    print(f"[*] Iniciando captura en la interfaz {INTERFACE}...")
    sniff_thread = threading.Thread(target=sniff_rssi, args=(num_paquetes, intervalo), daemon=True)
    sniff_thread.start()

    # Hilo para escuchar Beacons y enviar Probe Requests
    t_escuchar_beacons = threading.Thread(target=escuchar_beacons, daemon=True)
    t_escuchar_beacons.start()

    sock.sendall(f"INICIO_CAPTURA".encode())
    for i in range(num_paquetes + 1):
      time.sleep(intervalo)
      sock.sendall(f"Paquete {i+1}".encode()) 
      data = sock.recv(1024).decode() 
       
    stop_beacons = True
    sniff_thread.join()
    print("[CLIENT]: Captura de paquetes finalizada.")

  except Exception as e:
    sock.sendall(f"ERROR GENERAL: {e}".encode())


def main():
  print("[CLIENT]: Esperando que la interfaz gráfica se conecte.")
  #Variables para asegurar el correcto orden de ejecución
  sondeo_check = False
  cuantificacion_check = False
  reconciliacion_check = False
  amplificacion_check = False
  existe_conexion = False
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock_interfaz = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_interfaz.bind(('0.0.0.0',8000))
  sock_interfaz.listen(1)
  conn_i, addr_i = sock_interfaz.accept()
  print(f"[CLIENT]: Interfaz gráfica conectada ({addr_i}).")
 
  while True:
    print("[CLIENT]: Esperando a recibir un comando de la interfaz...")
    command = conn_i.recv(4096).decode() 
    comando = command.split(" ")[0]
    if comando == "SONDEO":
      if sondeo_check or cuantificacion_check or reconciliacion_check or amplificacion_check:
        print("[CLIENT]: ERROR. Orden de ejecución incorrecto.")
      else:
        num_paquetes = int(command.split(" ")[1])
        intervalo = int(command.split(" ")[2])
        print(f"[CLIENT]: Comando de sondeo recibido. Número de paquetes: {num_paquetes}, intervalo: {intervalo}")
        sock.connect((IP_SERVER,5000))
        print("[CLIENT]: Cliente conectado al servidor.")
        exchange_rssi(sock, num_paquetes, intervalo)
        sondeo_check = True
        sock.close()
        print("[CLIENT]: Sondeo del canal completado.")

    elif comando == "CUANTIFICACION":
      print("[CLIENT]: Comando de cuantificación recibido.")
      global server_secuencia, secuencia
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      if cuantificacion_check or reconciliacion_check or amplificacion_check:
        print("[CLIENT]: ERROR. Orden de ejecución incorrecto.")
      elif sondeo_check:
        valor_medio = media(RSSI_FILE)
        desviacion_tipica = desviacionTipica(valor_medio, RSSI_FILE)
        print(f"[CLIENT]: Valor medio utilizado para la etapa de cuantificacion: {valor_medio}.")
        #secuencia = cuantificacion(valor_medio, desviacion_tipica,0, RSSI_FILE)
        secuencia = cuantificacion_cuatro(valor_medio)
        print(f"[CLIENT]:Secuencia calculada por el CLIENT en la cuantificacion: {secuencia}.")
        sock.connect((IP_SERVER,5000))
        print("[CLIENT]: Cliente conectado al servidor.")
        server_secuencia = sock.recv(1024).decode()
        print(f"[CLIENT]: Secuencia recibida por el servidor: {server_secuencia}.")
        sock.sendall(secuencia.encode())
        sock.close()
        cuantificacion_check = True
        print("[CLIENT]: Cuantificación completada.")
      else:
        print("[CLIENT]: ERROR. No se ha realizado el sondeo del canal previamente.")

    elif comando == "RECONCILIACION":
      print("[CLIENT]: Comando de reconciliación recibido.")
      if amplificacion_check or reconciliacion_check:
        print("[SERVER]: ERROR. Orden de ejecución incorrecto. Ya se realizó esta etapa anteriormente.")
      elif cuantificacion_check:
        global secuencia_reconciliacion
        secuencia_reconciliacion = reconciliacion(secuencia, server_secuencia)
        print(f"[CLIENT]: Secuencia resultante tras la reconciliación: {secuencia_reconciliacion}.")
        reconciliacion_check = True

    elif comando == "AMPLIFICACION":
      print("[CLIENT]: Comando de amplificación recibido.")
      if amplificacion_check:
        print("[CLIENT]: ERROR. Orden de ejecución incorrecto. Esta etapa ya se ha realizado.")
      elif reconciliacion_check != True:
        print("[CLIENT]: ERROR. Debe realizar las etapas anteriores en el orden indicado.")
      else:
        clave_compartida = amplificacion(secuencia_reconciliacion)
        print(f"CLAVE COMPARTIDA GENERADA : {clave_compartida}")
        
    elif comando == "CERRAR":
      print("[CLIENT]: Cerrando programa")
      sock.close()
      sock_interfaz.close()
      sys.exit(0)
      break;
    else:
      print(f"[client] Comando desconocido: {command}. Cerrando programa.")
      sock.close()
      sock_interfaz.close()
      sys.exit(1)

    

if __name__ == "__main__":
    main()
