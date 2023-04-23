from machine import Pin, I2C
import dht, scd4x, network, time
from umqtt.simple import MQTTClient
from bme688 import *

""" I2C sensors """
i2c = I2C(id=0, scl=Pin(1), sda=Pin(0))
bme = BME680_I2C(i2c)
scd = scd4x.SCD4X(i2c)

""" One-Wire sensors """
d = dht.DHT11(machine.Pin(28))

""" Connect to Wi-Fi """
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ssid","password")
time.sleep(5)
print("Wi-Fi Connected?:")
print(wlan.isconnected())

"""Connect to MQTT broker """
mqtt_server = 'xxx.xxx.xxx.xxx'
client_id = "client_id"

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, port=1883, user="username", password="password", keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

""" MQTT topics """
temp_topic_pub = b"home/temperature"
rh_topic_pub = b"home/humidity"
bme_temp_topic_pub = b"home/bmetemp"
bme_rh_topic_pub = b"home/bmehumidity"
bme_pressure_topic_pub = b"home/bmepressure"
bme_gas_topic_pub = b"home/bmegas"
scd_co2_topic_pub = b"home/scdco2"
scd_temp_topic_pub = b"home/scdtemp"
scd_humid_topic_pub = b"home/scdhumid"

""" Set SCD41 to periodic measurement mode """
scd.start_periodic_measurement()

while True:
    if scd.data_ready:
        """ Command DHT11 to measure """
        d.measure()
        
        """Read SCD 41 data """
        scdtemp = scd.temperature
        scdhumid = scd.relative_humidity
        scdco2 = scd.CO2
        
        """Convert data to strings """
        scdco2 = str(scdco2)
        scdtemp = str(scdtemp)
        scdhumid = str(scdhumid)
        currenttemp = str(d.temperature())
        currenthumidity = str(d.humidity())
        bmetemp = str(bme.temperature)
        bmehumid = str(bme.humidity)
        bmepres = str(bme.pressure)
        bmegas = str(bme.gas)
        
        """Publish data to MQTT topics """
        client.publish(temp_topic_pub, currenttemp)
        client.publish(rh_topic_pub, currenthumidity)
        client.publish(bme_temp_topic_pub, bmetemp)
        client.publish(bme_rh_topic_pub, bmehumid)
        client.publish(bme_pressure_topic_pub, bmepres)
        client.publish(bme_gas_topic_pub, bmegas)
        client.publish(scd_co2_topic_pub, scdco2)
        client.publish(scd_temp_topic_pub, scdtemp)
        client.publish(scd_humid_topic_pub, scdhumid)
        
        """ Print data to terminal """
        print(f"SCD: CO2: {scdco2}; T: {scdtemp}; RH: {scdhumid}")
        print("DHT11: Temperature:", currenttemp, "Humidity:", currenthumidity)
        print("BME: Temp (C):", bmetemp, "RH (%)", bmehumid, "Pressure (hPa)", bmepres, "Gas:", bmegas)

