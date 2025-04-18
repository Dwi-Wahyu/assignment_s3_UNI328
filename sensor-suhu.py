from machine import Pin
import dht
import network
import time
import urequests
import json

# Konfigurasi Sensor
dht_sensor = dht.DHT11(Pin(4))
led = Pin(5, Pin.OUT)

# Konfigurasi WiFi
WIFI_SSID = "BA JO DAN"
WIFI_PASS = "8888dari"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        # Tunggu hingga terhubung (max 10 detik)
        timeout = 0
        while not wlan.isconnected():
            time.sleep(1)
            timeout += 1
            if timeout > 10:
                print("Gagal terhubung!")
                return False
    
    print("WiFi Terhubung!")
    print("IP Address:", wlan.ifconfig()[0])
    return True

# Fungsi Baca Sensor
def read_sensor():
    try:
        led.value(1)
      
        dht_sensor.measure()

        led.value(0)
        return {
            "temperature": dht_sensor.temperature(),
            "humidity": dht_sensor.humidity()
        }
    except Exception as e:
        print("Sensor Error:", e)
        return None

# Fungsi Kirim Data ke Backend
def send_to_backend(data):
    url = "http://192.168.1.16:5000/tambah"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = urequests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        print("Status Code:", response.status_code)
        response.close()
    except Exception as e:
        print("Gagal mengirim data:", e)

# Main Program
def main():
    if connect_wifi():
        while True:
            sensor_data = read_sensor()
            if sensor_data:
                print("Suhu: {}°C | Kelembaban: {}%".format(sensor_data['temperature'], sensor_data['humidity']))
                send_to_backend(sensor_data)
            
            time.sleep(5)  # Kirim data setiap 5 detik

main()