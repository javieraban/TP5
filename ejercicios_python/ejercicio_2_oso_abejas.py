import sys
import threading
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10
NUM_ABEJAS = 5
tarro_miel = 0
simulacion_activa = True

mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)


def abeja(id_abeja):
    global tarro_miel, simulacion_activa

    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))

        # Esperar a que el tarro esté disponible
        sem_tarro_disponible.acquire()

        with mutex:
            if not simulacion_activa:
                sem_tarro_disponible.release()
                break

            tarro_miel += 1

            print(
                f"🐝 Abeja {id_abeja} deposita miel "
                f"({tarro_miel}/{M})"
            )

            if tarro_miel == M:
                print("🍯 Tarro lleno. Se despierta al oso.")
                sem_oso.release()
                # NO liberamos sem_tarro_disponible:
                # el tarro queda bloqueado hasta que el oso lo vacíe
            else:
                sem_tarro_disponible.release()


def oso(max_tarros=2):
    global tarro_miel, simulacion_activa

    tarros_comidos = 0

    while tarros_comidos < max_tarros and simulacion_activa:

        # Espera pasiva hasta que el tarro esté lleno
        sem_oso.acquire()

        with mutex:
            print(
                f"🐻 Oso despierta y come "
                f"{tarro_miel} porciones de miel."
            )

            tarro_miel = 0
            tarros_comidos += 1

            print(
                f"🐻 Oso vació el tarro. "
                f"Tarros comidos: {tarros_comidos}"
            )

        # Ahora las abejas pueden volver a usar el tarro
        sem_tarro_disponible.release()

        time.sleep(0.05)

    simulacion_activa = False

    # Por seguridad, desbloqueamos posibles abejas esperando
    for _ in range(NUM_ABEJAS):
        sem_tarro_disponible.release()


if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
    print("=" * 60)

    hilo_oso = threading.Thread(target=oso)

    hilos_abejas = []

    for i in range(NUM_ABEJAS):
        hilo = threading.Thread(target=abeja, args=(i,))
        hilos_abejas.append(hilo)

    hilo_oso.start()

    for hilo in hilos_abejas:
        hilo.start()

    hilo_oso.join()

    for hilo in hilos_abejas:
        hilo.join()

    print("=" * 60)
    print(" Simulación finalizada")
    print("=" * 60)