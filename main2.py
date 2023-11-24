import bme680
import time
import psycopg2
import sys

# Creem una instància del sensor BME680
sensor = bme680.BME680()

# Configurar el sensor BME680
sensor.set_humidity_oversample(bme680.OS_8X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_2X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

# Després de calibrar el sensor, deixem un temps de calibratge
time.sleep(60)

# Dades de la base de dades per la seva connexió
# Les credencials són proporcionades per el script que s'executa cada cop
# que la raspberry fa un reboot
DADES_DB = {
    "host": "localhost",
    "user": str(sys.argv[1]),
    "password": str(sys.argv[2]),
    "dbname": str(sys.argv[3]),
    "port": 5432,
}


try:
    # Ens connectem a la base de dades
    connexio = psycopg2.connect(
        host=DADES_DB["host"],
        dbname=DADES_DB["dbname"],
        user=DADES_DB["user"],
        password=DADES_DB["password"],
        port=DADES_DB["port"],
    )
    # Creem una instància de cursor amb el qual podrem executar consultes sql
    cursor = connexio.cursor()

    # Creem el bucle infinit del programa, ja que no volem que funcioni indefinidament
    while True:
        # Si el sensor està disponible, procedim a accedir a les seves dades
        if sensor.get_sensor_data():
            temperature = sensor.data.temperature
            pressure = sensor.data.pressure
            humidity = sensor.data.humidity

            print(f"Temperatura: {temperature} °C")
            print(f"Presión: {pressure} hPa")
            print(f"Humedad: {humidity} %")

            # Insertem les variables la taula sensors_data de la BBDD
            cursor.execute(
                f"INSERT INTO sensors_data (temperatura, humitat, pressio) VALUES ({temperature}, {humidity}, {pressure})"
            )
            # Guardem els canvis realitzats a la BBDD
            connexio.commit()
        # Esperem 60 segons abans de realitzar la següent lectura
        time.sleep(60)

except KeyboardInterrupt:
    # Tanquem la connexió a la BBDD si hi ha algun error
    connexio.close()
    pass
