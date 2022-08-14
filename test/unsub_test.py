#!/usr/bin/python
import paho.mqtt.client as mqtt

broker_url = "localhost"
broker_port = 1883

LOG_FILE="/var/log/majd2mm.log"

def writeLog(logfile, logtext):
# write anything out to a log file
    logTime = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    logtext = logtext.rstrip()
    # makesure logtext always ends with a newline
    logtext += "\n";  
    logtext = logTime + " " + logtext;
    f = open(logfile,'a');
    f.write(logtext);
    f.close();

def on_connect(client,userData,flags, rc):
    msg = ("Test UnsubList Connected to MQTT with ResultCode %s"% rc)
    writeLog(LOG_FILE,msg)
client = mqtt.Client()
client.on_connect = on_connect
client.connect(broker_url, broker_port)

testPayload='{"email":"jomofrodo@gmail.com", "listName":"ccb_genrl"}'
client.publish(topic="UnsubList", payload=testPayload, qos=1, retain=False)
