"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 4: Monitores y Variables de Condición (El Barbero Dormilón)
Bibliografía de Referencia:
- Silberschatz: Cap. 6.7 (Monitores) y Cap. 6.6 (El problema del barbero dormilón)
- Diapositivas U5: Diapositiva 20 a 24 (Monitores y Problemas Clásicos)
"""

import sys
import threading
import time
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class BarberiaMonitor:
    def __init__(self, num_sillas_espera=3):
        self.num_sillas = num_sillas_espera
        self.clientes_esperando = 0

        self.lock = threading.Lock()

        self.cond_barbero = threading.Condition(self.lock)
        self.cond_sala_espera = threading.Condition(self.lock)
        self.cond_corte = threading.Condition(self.lock)

        self.silla_barbero_ocupada = False
        self.cliente_listo_en_sillon = False
        self.corte_terminado = False
        self.barberia_abierta = True

    def entrar_cliente(self, cliente_id):
        """
        Retorna True si el cliente fue atendido.
        Retorna False si la sala estaba llena.
        """
        with self.lock:
            print(
                f"👤 Cliente {cliente_id} llega a la barbería. "
                f"(Sillas ocupadas: {self.clientes_esperando}/{self.num_sillas})"
            )

            # Si la sala de espera está llena, el cliente se va
            if self.clientes_esperando >= self.num_sillas:
                print(
                    f"🚪 [SALA LLENA] Cliente {cliente_id} "
                    f"se va sin cortarse el pelo."
                )
                return False

            # Cliente ocupa una silla de espera
            self.clientes_esperando += 1

            print(
                f"🪑 Cliente {cliente_id} espera en la sala. "
                f"({self.clientes_esperando}/{self.num_sillas})"
            )

            # Despertar al barbero por si está dormido
            self.cond_barbero.notify()

            # Esperar mientras el sillón esté ocupado
            while self.silla_barbero_ocupada:
                self.cond_sala_espera.wait()

            # Pasar desde la sala de espera al sillón
            self.clientes_esperando -= 1
            self.silla_barbero_ocupada = True
            self.cliente_listo_en_sillon = True
            self.corte_terminado = False

            print(f"💺 Cliente {cliente_id} pasa al sillón del barbero.")

            # Avisar al barbero que el cliente ya está sentado
            self.cond_barbero.notify()

            # Esperar hasta que termine el corte
            while not self.corte_terminado:
                self.cond_corte.wait()

            print(f"✅ Cliente {cliente_id} terminó su corte.")

            # Cliente libera el sillón
            self.silla_barbero_ocupada = False
            self.cliente_listo_en_sillon = False
            self.corte_terminado = False

            # Avisar al barbero de que el cliente ya se levantó
            self.cond_barbero.notify()

            return True

    def atender_siguiente_cliente(self):
        """
        El barbero espera hasta que haya un cliente listo en el sillón.
        """
        with self.lock:
            while (
                not self.cliente_listo_en_sillon
                and self.barberia_abierta
            ):
                # Si hay clientes esperando y el sillón está libre,
                # permitir que uno pase
                if (
                    self.clientes_esperando > 0
                    and not self.silla_barbero_ocupada
                ):
                    self.cond_sala_espera.notify()

                print("😴 [Barbero] Esperando cliente...")
                self.cond_barbero.wait()

            # Si cerró la barbería y no hay cliente listo
            if (
                not self.barberia_abierta
                and not self.cliente_listo_en_sillon
            ):
                return False

            return True

    esperar_cliente_para_corte = atender_siguiente_cliente

    def finalizar_corte(self):
        """
        El barbero avisa que terminó el corte y espera
        hasta que el cliente abandone el sillón.
        """
        with self.lock:
            self.corte_terminado = True

            print("✂️ [Barbero] Corte terminado.")

            # Despertar al cliente que está esperando el fin del corte
            self.cond_corte.notify()

            # Esperar hasta que el cliente se levante
            while self.silla_barbero_ocupada:
                self.cond_barbero.wait()

            # Recién ahora permitir que pase otro cliente
            if self.clientes_esperando > 0:
                self.cond_sala_espera.notify()

    def cerrar_barberia(self):
        with self.lock:
            self.barberia_abierta = False

            self.cond_barbero.notify_all()
            self.cond_sala_espera.notify_all()
            self.cond_corte.notify_all()


def hilo_barbero(barberia):
    while True:
        hay_cliente = barberia.atender_siguiente_cliente()

        if not hay_cliente:
            break

        print("✂️ [Barbero] Cortando el cabello...")
        time.sleep(random.uniform(0.1, 0.25))

        barberia.finalizar_corte()


def hilo_cliente(barberia, cliente_id):
    time.sleep(random.uniform(0.05, 0.3))
    barberia.entrar_cliente(cliente_id)


if __name__ == "__main__":
    print("=" * 60)
    print(" Barbería con Monitores y Variables de Condición (UNJu FI)")
    print("=" * 60)

    barberia = BarberiaMonitor(num_sillas_espera=3)

    t_barbero = threading.Thread(
        target=hilo_barbero,
        args=(barberia,),
        name="Barbero"
    )

    t_barbero.start()

    clientes = []

    for i in range(1, 9):
        t_cli = threading.Thread(
            target=hilo_cliente,
            args=(barberia, i),
            name=f"Cliente-{i}"
        )

        clientes.append(t_cli)
        t_cli.start()

    for t_cli in clientes:
        t_cli.join()

    time.sleep(0.5)

    barberia.cerrar_barberia()
    t_barbero.join()

    print("=" * 60)
    print(" Simulación de Barbería finalizada.")
    print("=" * 60)