"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 5: Lectores - Escritores
"""

import sys
import threading
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ============================================================================
# VARIABLES COMPARTIDAS Y SEMÁFOROS
# ============================================================================

mutex = threading.Semaphore(1)
sem_write = threading.Semaphore(1)

readcounter = 0

base_de_datos = {
    "version": 1,
    "contenido": "Datos iniciales consistentes del sistema operativo."
}

print_lock = threading.Lock()


def log(msg):
    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ============================================================================
# PROCESO LECTOR
# ============================================================================

def lector(id_lector, iteraciones=2):
    global readcounter

    for _ in range(iteraciones):

        time.sleep(random.uniform(0.1, 0.4))

        # ------------------------------------------------------------
        # ENTRADA DEL LECTOR
        # ------------------------------------------------------------

        mutex.acquire()

        readcounter += 1

        # El primer lector bloquea a los escritores
        if readcounter == 1:
            sem_write.acquire()

        mutex.release()

        # ------------------------------------------------------------
        # SECCIÓN DE LECTURA
        # ------------------------------------------------------------

        log(
            f"📖 Lector {id_lector} LEYENDO datos "
            f"(v{base_de_datos['version']}) | "
            f"Lectores activos: {readcounter}"
        )

        time.sleep(random.uniform(0.2, 0.5))

        log(f"✨ Lector {id_lector} terminó de leer.")

        # ------------------------------------------------------------
        # SALIDA DEL LECTOR
        # ------------------------------------------------------------

        mutex.acquire()

        readcounter -= 1

        # El último lector libera la BD
        if readcounter == 0:
            sem_write.release()

        mutex.release()


# ============================================================================
# PROCESO ESCRITOR
# ============================================================================

def escritor(id_escritor, iteraciones=2):
    global base_de_datos

    for _ in range(iteraciones):

        time.sleep(random.uniform(0.3, 0.7))

        log(
            f"⏳ Escritor {id_escritor} "
            f"solicitando permiso para escribir..."
        )

        # Acceso exclusivo
        sem_write.acquire()

        # ------------------------------------------------------------
        # SECCIÓN CRÍTICA DE ESCRITURA
        # ------------------------------------------------------------

        nueva_version = base_de_datos["version"] + 1

        log(
            f"✍️ [EXCLUSIÓN MUTUA] Escritor {id_escritor} "
            f"MODIFICANDO la BD a versión {nueva_version}..."
        )

        time.sleep(random.uniform(0.3, 0.6))

        base_de_datos["version"] = nueva_version

        base_de_datos["contenido"] = (
            f"Registro actualizado por escritor {id_escritor} "
            f"a las {time.strftime('%H:%M:%S')}"
        )

        log(
            f"✅ Escritor {id_escritor} "
            f"finalizó escritura de versión {nueva_version}."
        )

        # Liberar para otro escritor o grupo de lectores
        sem_write.release()


# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("EJERCICIO 5: Lectores y Escritores (Algoritmo de Courtois)")
    print("=" * 70)

    hilos = []

    # 5 lectores
    for i in range(1, 6):
        t = threading.Thread(
            target=lector,
            args=(i,)
        )
        hilos.append(t)

    # 2 escritores
    for j in range(1, 3):
        t = threading.Thread(
            target=escritor,
            args=(j,)
        )
        hilos.append(t)

    # Mezclar el orden de arranque
    random.shuffle(hilos)

    for t in hilos:
        t.start()

    for t in hilos:
        t.join()

    print(
        "\nSimulación finalizada. "
        "Estado final de la BD:",
        base_de_datos
    )