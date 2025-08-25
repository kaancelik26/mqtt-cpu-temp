import time
import requests
import paho.mqtt.client as mqtt

URL = "http://localhost:8085/data.json"      #bağlantı kısmım web tabanlı oldugu için
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "pc/sicaklik"
MQTT_QOS = 1

def find_cpu_package_temperature(node):        #sıcaklığı json için bulma  fonksiyonu
    if not isinstance(node, dict):
        return None

    if node.get("Text", "").lower() == "temperatures":              #cpu sıcakılığını arayan bölüm
        for sensor in node.get("Children", []):
            if sensor.get("Text", "").lower() == "cpu package":
                value = sensor.get("Value")
                if value:
                    try:
                        return float(value.split()[0].replace(',', '.'))    #bulununan sıcaklığı float veri tipine dönüşür
                    except:
                        return None

    for child in node.get("Children", []): #başka alt sıcaklık türü olabilir en alt seviyeye kadar incelemek için
        result = find_cpu_package_temperature(child)
        if result is not None:
            return result

    return None

def on_connect(client, userdata, flags, rc): #mqtt otamatik olarak çalıştıracak fonksiyon
    if rc == 0:
        print("MQTT bağlantısı başarılı.")
    else:
        print(f"MQTT bağlantı hatası: {rc}")

client = mqtt.Client()    #mqtt istemcisini başlatma kısımı
client.on_connect = on_connect
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("CPU sıcaklığı ölçümü başlıyor...")
#ana döngümüz
try:
    while True:
        try:
            response = requests.get(URL, timeout=5)   #json verileri çekme
            data = response.json()

            temp = find_cpu_package_temperature(data)   #cpu sıcaklığını buldma
            if temp is not None:
                print(f"CPU Package Sıcaklığı: {temp} °C")   #mqtt bağlantısı
                client.publish(MQTT_TOPIC, temp, qos=MQTT_QOS)
            else:
                print("CPU sıcaklığı bulunamadı.")
        except Exception as e:
            print(f"Hata: {e}")
        time.sleep(5) #veriyi kaç saniyede alacağımız

except KeyboardInterrupt:
    print("Program durduruldu.")
    client.loop_stop()
    client.disconnect()



#& "C:\Program Files\mosquitto\mosquitto_sub.exe" -h test.mosquitto.org -t pc/sicaklik -v
