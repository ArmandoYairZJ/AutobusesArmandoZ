import telepot
import RPi.GPIO as GPIO
import time
import sqlite3
from pirc522 import RFID
from threading import Thread

GPIO.setwarnings(False)
6800650169:AAFKH1KK3bYPBIhdPIqZ9x5ZWpoZ-kfbOT8
bot_token = '6616690178:AAGE4fWbaVP6FKH9ifCDJrH9_4w1mfq2g08'
bot = telepot.Bot(bot_token)

rc522 = RFID()
print('Bienvenido Autobuses Armando y el camarada Angel')

def insertar_acceso(pin, tipo):
    try:
        conn = sqlite3.connect('/home/armangel/mu_code/Cam.db')
        cursor = conn.cursor()

        if tipo == 'alumno':
            cursor.execute("INSERT INTO Alumnos(PinAlumno) VALUES (?)", (pin,))
        elif tipo == 'persona':
            cursor.execute("INSERT INTO Personas(PinPersonas) VALUES (?)", (pin,))

        cursor.execute("INSERT INTO VIAJAS(PIN_ALUMNO, PIN_PERSONA) VALUES (?, NULL)", (pin,))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
    finally:
        conn.close()

def enviar_mensaje(chat_id, mensaje):
    bot.sendMessage(chat_id, mensaje)

def generar_reporte():
    try:
        conn = sqlite3.connect('/home/armangel/mu_code/Cam.db')
        cursor = conn.cursor()

        # Get the total number of trips
        cursor.execute("SELECT COUNT(*) FROM VIAJAS")
        total_trips = cursor.fetchone()[0]

        # Get the total number of student trips
        cursor.execute("SELECT COUNT(*) FROM ALumnos")
        total_students = cursor.fetchone()[0]

        # Get the total number of normal people trips
        cursor.execute("SELECT COUNT(*) FROM Personas")
        total_normal_people = cursor.fetchone()[0]

        conn.close()

        # Calculate the total cost
        total_cost_students = total_students * 3.5
        total_cost_normal_people = total_normal_people * 13
        total_cost_final = total_cost_students + total_cost_normal_people

        report_text = f"Total de Viajes: {total_trips}\n"
        report_text += f"Total de Viajes de Alumnos: {total_students}. Costo total: {total_cost_students} pesos.\n"
        report_text += f"Total de Viajes de Personas Normales: {total_normal_people}. Costo total: {total_cost_normal_people} pesos.\n"
        report_text += f"Costo total de todos los Viajes: {total_cost_final} pesos."

        return report_text
    except Exception as e:
        print(f"Error al generar el reporte: {e}")

def handle(msg):
    chat_id = msg['chat']['id']
    text = msg['text']

    try:
        if text.startswith('/totalAlumnos'):
            conn = sqlite3.connect('/home/armangel/mu_code/Cam.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ALumnos")
            total_alumnos = cursor.fetchone()[0]
            conn.close()
            total_costo_alumnos = total_alumnos * 3.5
            enviar_mensaje(chat_id, f"Total de alumnos registrados: {total_alumnos}. Costo total: {total_costo_alumnos} pesos.")

        elif text.startswith('/totalPersonas'):
            conn = sqlite3.connect('/home/armangel/mu_code/Cam.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Personas")
            total_personas = cursor.fetchone()[0]
            conn.close()
            total_costo_personas = total_personas * 13
            enviar_mensaje(chat_id, f"Total de personas registradas: {total_personas}. Costo total: {total_costo_personas} pesos.")

        elif text.startswith('/total'):
            conn = sqlite3.connect('/home/armangel/mu_code/Cam.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM VIAJAS")
            total_TOTAL = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM ALumnos")
            total_alumnos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Personas")
            total_personas = cursor.fetchone()[0]
            conn.close()

            total_costo_alumnos = total_alumnos * 3.5
            total_costo_personas = total_personas * 13
            total_final = total_costo_alumnos + total_costo_personas

            enviar_mensaje(chat_id, f"Total de Viajes: {total_TOTAL}. Costo total: {total_final} pesos.")

        elif text.startswith('/reporte'):
            report_text = generar_reporte()
            if report_text:
                enviar_mensaje(chat_id, report_text)
            else:
                enviar_mensaje(chat_id, "Error al generar el reporte.")

        else:
            enviar_mensaje(chat_id, "Comando no reconocido")
    except Exception as e:
        print(f"Error al manejar el mensaje: {e}")

def rfid_loop():
    try:
        while True:
            rc522.wait_for_tag()
            (error, tag_type) = rc522.request()

            if not error:
                (error, uid) = rc522.anticoll()

                if not error:

                    pin = '-'.join(map(str, uid))

                    if uid == [243, 164, 109, 252, 198]:
                        print('Estudiante costo 3.5 pesos.')
                        insertar_acceso(pin, 'alumno')

                    elif uid == [227, 150, 245, 246, 118]:
                        print('Persona Normal costo 13 pesos.')
                        insertar_acceso(pin, 'persona')
                    else:
                        print('Unknown badge. No specific action taken.')

                    time.sleep(1)
    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario.")
    finally:
        rc522.cleanup()
        GPIO.cleanup()

# Crear un hilo para el bucle RFID
rfid_thread = Thread(target=rfid_loop)

# Iniciar ambos hilos
rfid_thread.start()
bot.message_loop(handle)

# Esperar hasta que ambos hilos terminen
rfid_thread.join()