# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025

import tkinter as tk
import hashlib

def calcular_hash(secuencia):
  return hashlib.sha256(secuencia.encode()).hexdigest()
 
 
def checkHashes(hash_cliente, hash_servidor):
    if hash_cliente != hash_servidor:
        return True
    else:
        return False

# Función que calcula la paridad, devuelve cero si el número de 1 es par.
def calcularParidad(bits):
  return sum(bits) % 2 

# Paso 3: Reconciliación.
def reconciliar(mi_secuencia, su_secuencia):
  secuencia = []
  for i in range(len(mi_secuencia)):
    if mi_secuencia[i] == su_secuencia[i]:
      secuencia.append(mi_secuencia[i])
    else:
      secuencia.append('0')
  paridadA = calcularParidad([int(bit) for bit in mi_secuencia])
  paridadB = calcularParidad([int(bit) for bit in su_secuencia])
  if paridadA != paridadB:
      print("[SERVER]: ERROR. Ha habido un error en la reconciliación.")
  return secuencia

def metricaHamming(secuencia_server, secuencia_client):
  assert(len(secuencia_server) == len(secuencia_client))
  return sum(bit1 != bit2 for bit1,bit2 in zip(secuencia_server, secuencia_client))
  
def generarInfoReconciliacion(frame, secuencia_reconciliada, secuencia_server, secuencia_client):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la reconciliación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Secuencia de A", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_server, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_client, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de bits reconciliada", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_reconciliada, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Métrica de Hamming", bg="white").pack(pady=5)
  tk.Label(recuadro, text=metricaHamming(secuencia_server, secuencia_client), bg="white").pack(pady=5)
  
def iniciarReconciliacion(conn, secuencia):
  secuencia_final = list("0000000000000000")
  secuencia = list(secuencia)
  hash_recibido= conn.recv(1024).decode()
  hash_calculado = calcular_hash(''.join(secuencia))
  print("he recibido", hash_recibido)
  print("he calculado", hash_calculado)
  if hash_calculado == hash_recibido:
    secuencia_final = secuencia
    conn.sendall("Coinciden".encode())
    return
  else:
    conn.sendall("Continuar".encode())
  secuencia_final=reconciliacion(conn, secuencia)
  print("Secuencia final reconciliada", ''.join(secuencia_final))
  conn.sendall("Fin de transmisión".encode())
  return secuencia_final
  
def reconciliacion(conn, mi_secuencia, mitad=16):
  print("mitad", mitad)
  while True:
    mitad = mitad // 2
    if mitad == 1:
      hash_cliente = conn.recv(1024).decode()
      primera_mitad = mi_secuencia[:mitad]
      segunda_mitad = mi_secuencia[mitad:]
      hash_primera = calcular_hash(''.join(primera_mitad))
      hash_segunda = calcular_hash(''.join(segunda_mitad))
      hashes = hash_cliente.split(",")
      continuar_primera = checkHashes(hashes[0], hash_primera)
      continuar_segunda = checkHashes(hashes[1], hash_segunda)
      
      if continuar_primera:
        if mi_secuencia[0] == "0":
           mi_secuencia[0] = "1"
        else:
          mi_secuencia[0] = "0"
      if continuar_segunda:
        if mi_secuencia[1] == "0":
          mi_secuencia[1] = "1"
        else:
          mi_secuencia[1] = "0"
      conn.sendall("Fin".encode())
      return ''.join(mi_secuencia)
        
    primera_mitad = mi_secuencia[:mitad]
    segunda_mitad = mi_secuencia[mitad:]
    hash_primera = calcular_hash(''.join(primera_mitad))
    hash_segunda = calcular_hash(''.join(segunda_mitad))
    respuesta = conn.recv(1024).decode()
    hashes = respuesta.split(",")
    print("mi_primera", hash_primera, hashes[0])
    print("segunda", hash_segunda, hashes[1])
    continuar_primera = checkHashes(hashes[0], hash_primera)
    continuar_segunda = checkHashes(hashes[1], hash_segunda)
        
    if continuar_primera and continuar_segunda:
      conn.sendall(" Continuar ambas".encode())
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
    elif continuar_primera:
      conn.sendall(" Continuar primera".encode())
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
    elif continuar_segunda:
      conn.sendall(" Continuar segunda".encode())
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
    else:
      conn.sendall(" Coinciden".encode())
    primera_mitad=list(primera_mitad)
    segunda_mitad=list(segunda_mitad)
    return primera_mitad + segunda_mitad
