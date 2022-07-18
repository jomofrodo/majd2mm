#!/usr/bin/python
'''
Created on Jul 17, 2022

@author: John Moore,  jmoore@netazoic.com

majd2mm.mjdprocess -- Process majordomo style email commands posted to the mqtt queue

'''

import os
import re
import subprocess
import shlex
import time
import sys
import datetime
import pwd
import paho.mqtt.client as mqtt
import json

#import pdb
#pdb.set_trace()

email_body = "";
cmd = "";
domainName = "mm2.freeburmarangers.org";
line = "";
fromAddr = "";
broker_url = "localhost"
broker_port = 1883

cmdMM = "";
logMsg = "";
flgUnsub = 0;
flgDebug = 0;


#************* SET THESE VALUES **************
MM_BIN = "/usr/lib/mailman/bin";
MEMBERS_FILE = "./members.txt";
LIST = "ccb_genrl";
LOG_FILE = "/var/log/majd2mm.log";
TEST_FILE = "./test/test.forward.txt"
user_name = "fbr.mailadmin"
#********************************************
binFileExists = os.path.isdir(MM_BIN)
if(not binFileExists):
     if(not flgDebug): 
         exit("The mailman bin directory not located. Please edit settings.");
         
def on_connect(client,userData,flags, rc):
    msg = ("Connected to MQTT with ResultCode %s"% rc)
    writeLog(LOG_FILE,msg)


def writeLog(logfile, logtext):
# write anything out to a log file
    logTime = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    logtext = logtext.rstrip()
    # makesure logtext always ends with a newline
    logtext += "\n";  
    logtext = logTime + " " + logtext;
    if(flgDebug): print(logtext);
    f = open(logfile,'a');
    f.write(logtext);
    f.close();

def writeMembers(email):
    # Write email out to a members file
    f = open(MEMBERS_FILE,'w');
    f.write(email)
    f.close();


client = mqtt.Client();
client.on_connect = on_connect
client.connect(broker_url, broker_port)

def on_subscribe(client,userData,message):
    rec = json.loads(message.payload);
    email = rec['email']
    listName = rec['listName']
    # just run the add_members command
    cmd = " %s/add_members -r %s " %(MM_BIN,MEMBERS_FILE);
    cmd += " --welcome-msg=yes --admin-notify=no ";
    cmd += listName 
    args = shlex.split(cmd)
    writeLog(LOG_FILE, args);
    ret = ""
    try:
            ret = subprocess.check_output(cmd, shell=True)
            logMsg = listName + ": " + ret
    except subprocess.CalledProcessError:
            logMsg = "Error while trying to subscribe %s to %s\n" % (email, listName);
            logMsg += ret;
    writeLog(LOG_FILE,logMsg)
            
def on_unsubscribe(client,userData,message):
     lists = []
     rec = {}
     try:
     	rec = json.loads(message.payload);
     except JSONDecodeError:
        print ("Could not json parse message.payload");
     email = rec['email']
     listName = rec['listName']
     email = email.replace("\*", "");  # remove wildcards in the email address
     cmd = "%s/remove_members " % MM_BIN;
     if(listName == "*"):
        cmd += " --fromall";
        lists = [listName]
     else:
        if(re.match(".*\|", listName)):
            lists = listName.split("|")
        else:
            lists = [listName]
        for ln in lists:
	    result = ""
            cmd1 = cmd;
            cmd1 += ln + " "
            cmd1 += email
	    try:
		result = subprocess.check_output(cmd1.split(" "))
                logMsg = "Unsubscribed %s from %s" % (email, ln)
		next
	    except subprocess.CalledProcessError:
                logMsg = "Error while trying to unsubscribe %s from %s\n" % (email, ln);
                logMsg += "%s \n" % result 
        
            writeLog(LOG_FILE, logMsg);
    
    ### End of on_unsubscribe
    
### MQTT subscriptions

client.subscribe("SubscribeList")
client.subscribe("UnsubList")
client.message_callback_add("SubscribeList", on_subscribe)
client.message_callback_add("UnsubList", on_unsubscribe)

client.loop_forever() 


    
