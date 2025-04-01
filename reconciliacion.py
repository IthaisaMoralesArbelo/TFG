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
def iniciarReconciliacion(sock, secuencia):
  secuencia = list(secuencia)
  hash_calculado = calcular_hash(''.join(secuencia))
  print("Le envio mi hash")
  sock.sendall(hash_calculado.encode())
  while True:
    data = sock.recv(1024).decode().strip()
    print("recibo:", data)
    if not data:
      print("Error. El servidor no ha respondido")
      break;
    if data == " Coinciden":
      return
    elif data == "Fin de transmisión":
      return secuencia
    secuencia = reconciliacion(sock, secuencia)
  secuencia_final = ''.join(secuencia)
  return secuencia_final
def reconciliacion(conn, mi_secuencia, mitad=16):
  print(" Entro recursiva")
  while True:
    if len(mi_secuencia) == 1:
      return mi_secuencia
    
    mitad = mitad // 2
    primera_mitad = mi_secuencia[:mitad]
    segunda_mitad = mi_secuencia[mitad:]
    hash_primera = calcular_hash(''.join(primera_mitad))
    hash_segunda = calcular_hash(''.join(segunda_mitad))
    conn.sendall(f"{hash_primera},{hash_segunda}".encode())
    respuesta = conn.recv(1024).decode().strip()
    if respuesta == "Continuar primera":
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Continuar segunda":
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Continuar ambas":
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Coinciden":
      return mi_secuencia
    else:
      return mi_secuencia
        

