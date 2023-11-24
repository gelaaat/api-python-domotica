from flask import Flask, request, abort, jsonify
import RPi.GPIO as GPIO
import time

# Creem una instància del servidor web Flask
app = Flask(__name__)

# Declarem les variables "globals" i configuracions de pins
pin_17 = 17
pin_18 = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_17, GPIO.OUT)
GPIO.setup(pin_18, GPIO.OUT)

TRIG_PIN = 23
ECHO_PIN = 24
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Declarem la url que tindrà accés a aquesta api
allowed_origin = "http://localhost:5173"


# Verifiquem que les peticions que arriben sigui del domini correcte
@app.before_request
def check_origin():
    if "Origin" in request.headers:
        if request.headers["Origin"] != allowed_origin:
            abort(403)


# Aquesta funció s'encarrega del control dels pins
@app.route("/controlPin", methods=["GET"])
def encender_led():
    pin_number = request.args.get("pin")
    estat_a_posar = request.args.get("estat")
    if pin_number == "17" and estat_a_posar == "true":
        GPIO.output(pin_17, GPIO.HIGH)
        return jsonify({"data": "true"})
    elif pin_number == "18" and estat_a_posar == "true":
        GPIO.output(pin_18, GPIO.HIGH)
        return jsonify({"data": "true"})
    elif pin_number == "17" and estat_a_posar == "false":
        GPIO.output(pin_17, GPIO.LOW)
        return jsonify({"data": "false"})
    elif pin_number == "18" and estat_a_posar == "false":
        GPIO.output(pin_18, GPIO.LOW)
        return jsonify({"data": "false"})
    else:
        # Si la petició s'especifica un pin no declarat, es retorna 404
        abort(404)


# Aquesta funció és la que li diu a la pàgina web en quin estat està l'interruptor
# És pel primer renderitzat del panell de control de pins
@app.route("/estatPin", methods=["GET"])
def estat_pin():
    pin_id = request.args.get("pinId")
    if pin_id == "17":
        pin_status = GPIO.input(pin_17)
        return jsonify({"data": pin_status})
    elif pin_id == "18":
        pin_status = GPIO.input(pin_18)
        return jsonify({"data": pin_status})
    else:
        abort(404)


# Aquesta funció càlcula el nivell del dipòsit
@app.route("/nivellDiposit", methods=["GET"])
def nivell_diposit():
    # Ens assegurem que el transmissor ultrasònic no està emetens senyals
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(2)

    # Enviem una senyal pel transmissor i el tornem a apagar
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # El receptor comença a escoltar, guardem el temps de començament
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start_time = time.time()

    # Quan es rep senyal, es guarda el temps
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end_time = time.time()

    # Calculem la durada del senyal en anar i tornar
    pulse_duration = pulse_end_time - pulse_start_time

    # Calculem la distància multiplicant ka duració per la velocitat del so en l'aire i dividim per 2
    # perquè la senyal ha anat i ha tornat i només volem la distància d'anada per exemple
    distance = (pulse_duration * 34300) / 2

    # Especifiquem l'altura del dipòsit i calculem el seu nivell
    tank_height = 1.5
    level_percentage = (1 - (distance / tank_height)) * 100

    # Retornem un JSON amb el % del dipòsit
    return jsonify({"data": level_percentage})


# Aquesta funció és la handler d'errors del servidor, si algo falla enviem resposta 500
@app.errorhandler(500)
def internal_server_error(e):
    return "", 500


# Executem l'aplicació directament ja que no s'utilitza com un paquet
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
