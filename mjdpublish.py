#!/usr/bin/python
'''
Created on Jul 17, 2022

@author: John Moore,  jmoore@netazoic.com

majd2mm.mjdpublish -- Publish majordomo style email processing commands to the mqtt pubsub queue

Currently, supports subscribe (to a list) and unsubscribe (from a  list)
'''

import os
import re
import subprocess
import time
import sys
import datetime
import pwd
import paho.mqtt.client as mqtt

#import pdb
#pdb.set_trace()

email_body = "";
cmd = "";
domainName = "mm2.freeburmarangers.org";
line = "";
fromAddr = "";
broker_url="localhost"
broker_port = 1883

cmdMM = "";
logMsg = "";
flgUnsub = 0;
flgDebug = 0;

client = mqtt.Client()
client.connect(broker_url,broker_port);

#************* SET THESE VALUES **************
LIST = "ccb_genrl";
LOG_FILE = "/var/log/majd2mm.log";
TEST_FILE = "./test/test.forward.txt"
user_name = "fbr.mailadmin"
#********************************************

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


def publishCmd(cmd):
 # Publish a mosquitto command to subscribe or unsubscribe
    lists = []

    if(re.search("^approve.*", cmd)):
        regex = "approve\s+([\w|\.]+)\s+([\w]+)\s+([\w|_|\.|\*]+)\s+([\w|_|@|\.]+)"
        m = re.search(regex, cmd);
        passwd = m.group(1);
        cmdVerb = m.group(2);
        listName = m.group(3);
        email = m.group(4);
	payload = '{"listName":%s,"email":%s}'%(listName,email)
	client.publish(topic="SubscribeList", 
		payload=payload )

    elif(re.search("^unsubscribe.*", cmd)):
        regex = "^unsubscribe\s+([\w|_|\*|\|]+)\s+(.*)"
        m = re.search(regex, cmd);
        cmdVerb = "unsubscribe";
        listName = m.group(1);
        email = m.group(2);
	payload = '{"listName":"%s","email":"%s"}'% (listName,email)
	
	client.publish(topic="UnsubList", payload=payload)

    else:
        cmdVerb = "ERROR";
        logMsg = "problem processing: " + cmd;
        return;

    
    ### End of publishCmd
    
    
## Process the FILE (email)


if(flgDebug):
    inputFile = TEST_FILE
else:
    inputFile = sys.stdin
    
#for line in open(inputFile):
for line in sys.stdin:
    if(True): 
        print(line)
    email_body += line
    line = line.rstrip();
    m = re.search("^\s*From:.*[\s:\<]\s*([\w\.]+@[\w\.]+)", line)
    if(m):
        fromAddr = m.group(1)
        next
    # check for a command
    m = re.search("^\s*?(approve|unsubscribe).*", line)
    if(m):
        cmd = line
        publishCmd(cmd)
        continue

    # check for an unsubscribe in email
    m = re.search("^\s*?Subject:.*(unsub|remove)", line, re.IGNORECASE)
    #m = re.search("^Subject:.*", line)
    if(m):
        flgUnsub = 1;
        # Have to process this command outside the main loop as we can't be sure
        # the subject line will follow the From line
        # $cmd = "approve ccb.passwd unsubscribe * $from";
        # processCmd($cmd);
        next;

    m = re.search("^\s*remove\s*", line, re.IGNORECASE)
    if(m):
        flgUnsub = 1;
        next;

    # check for an END_PROCESSING command
    m = re.search("^end$", line)
    if(m):
        break
    
    next;

if(flgUnsub and not fromAddr.isspace()):
# Special purpose -- process a user submitted remove or unsub command
        cmd = "unsubscribe ccb_genrl|ccb_specl|ccb_prayer %s" % fromAddr;
        publishCmd(cmd);
        flgUnsub = 0;

