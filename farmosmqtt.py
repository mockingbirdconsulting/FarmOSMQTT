
#!/usr/bin/env python
import json
import yaml
import time
from datetime import datetime
import socket
import paho.mqtt.client as paho
import mysql.connector
import requests
import phpserialize

# Read in the config
with open('/etc/farmosmqtt/config.yml') as cfg_file:
    cfg = yaml.safe_load(cfg_file)
   

dbcx = mysql.connector.connect(
        host=cfg['database']['host'],
        user=cfg['database']['user'],
        passwd=cfg['database']['password'],
        database=cfg['database']['db_name']
        )


mqbroker = cfg['mqtt']['host']
mqport = cfg['mqtt']['port']
mqusername = cfg['mqtt']['user']
mqpassword = cfg['mqtt']['password']

# Set the MQTT topic based on the server type
if cfg['lora']['server_type'] == "ttn":
   mqtopic = "+/devices/+/up"
elif cfg['lora']['server_type'] == "loraserverio":
#   mqtopic = "application/%s/#" % cfg['lora']['app_id']
   mqtopic = "application/#"

mqc = paho.Client()
if cfg['lora']['use_tls'] == True:
    mqc.tls_set(ca_certs = cfg['lora']['cert_path'])

mqc.username_pw_set(mqusername, mqpassword)

def convert(data):
    if isinstance(data, bytes):  return data.decode('ascii')
    if isinstance(data, dict):   return dict(map(convert, data.items()))
    if isinstance(data, tuple):  return map(convert, data)
    return data

def build_sensor_url(sensor_name):
    host = cfg['farmos']['host']
    sensor_sql = """
    SELECT settings
    FROM farm_asset
    INNER JOIN 
        farm_sensor 
        ON farm_asset.id = farm_sensor.id
    WHERE farm_asset.type = 'sensor'
    AND name LIKE '%%%s%%'
    """ % sensor_name
    sensor_db_cur = dbcx.cursor()
    sensor_db_cur.execute(sensor_sql)
    sensor_res = sensor_db_cur.fetchall()
    sensor_settings = {}
    if len(sensor_res) > 1:
        print("More than one matching sensor found")
    elif len(sensor_res) == 0:
        print("No devices matching %s found in database" % sensor_name)
        print("Query was: %s" % sensor_sql)
    else:
        sensor_settings = convert(phpserialize.unserialize(sensor_res[0][0].encode()))
        url = "%s/farm/sensor/listener/%s?private_key=%s" % (
                                                             host,
                                                             sensor_settings['public_key'],
                                                             sensor_settings['private_key']
                                                            )
        return url
    

def on_connect(client, userdata, flags, rc):
    mqc.subscribe(mqtopic) 

def on_message(client, userdata, msg):
    message = json.loads(msg.payload)
    # LoRaServer.io Config
    if cfg['lora']['server_type'] == "loraserverio":
        if "deviceName" in message:
            surl = build_sensor_url(message['deviceName'])
            sensors = message['object']
            sensors['timestamp'] = datetime.now().timestamp()
            r = requests.post(
                url = surl,
                data = json.dumps(sensors)
            )
        else:
            print("Device name not found in message")

mqc.on_connect = on_connect
mqc.on_message = on_message


mqc.connect(mqbroker, mqport, 60)
mqc.loop_forever()

