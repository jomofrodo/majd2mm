#!/usr/bin/python
'''
Created on Jul 11, 2022

@author: John Moore,  jmoore@netazoic.com

majd2mm.majd2mm -- Add majordomo style email processing to the mailman system

majd2mm.majd2mm is a conversion of the majd2mm.pl perl script, 
             the purpose of which is to convert majordomo email commands to mailman email commands
             Primarily used for unsubscribe
'''

import os
import re
import subprocess
import time
import sys
import datetime
import pwd

#import pdb
#pdb.set_trace()

email_body = "";
cmd = "";
domainName = "mm2.freeburmarangers.org";
line = "";
fromAddr = "";

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
         
pw_record = pwd.getpwnam(user_name)
user_name      = pw_record.pw_name
user_home_dir  = pw_record.pw_dir
user_uid       = pw_record.pw_uid
user_gid       = pw_record.pw_gid

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


def writeMembers(members):
    memfile = MEMBERS_FILE;
    f = open(memfile)
    # zero it out
    f.delete();    
    f.write(members);
    f.close();


def processCmd(cmd):
    lists = []

    if(re.search("^approve.*", cmd)):
        regex = "approve\s+([\w|\.]+)\s+([\w]+)\s+([\w|_|\.|\*]+)\s+([\w|_|@|\.]+)"
        m = re.search(regex, cmd);
        passwd = m.group(1);
        cmdVerb = m.group(2);
        listName = m.group(3);
        email = m.group(4);

    elif(re.search("^unsubscribe.*", cmd)):
        regex = "^unsubscribe\s+([\w|_|\*|\|]+)\s+(.*)"
        m = re.search(regex, cmd);
        cmdVerb = "unsubscribe";
        listName = m.group(1);
        email = m.group(2);

    else:
        cmdVerb = "ERROR";
        logMsg = "problem processing: " + cmd;
        return;

    # Just run commands directly
    
    if(cmdVerb == "subscribe"):
        # just run the add_members command
        # cmd = " %s/add_members -r %s " %(MM_BIN,MEMBERS_FILE);
        cmd = " %s/sub " % (MM_BIN);
        cmd += " -w y -a n ";
        cmd += listName + " " + email
	try:
            ret = subprocess.check_output([cmd,'-w y', '-a n', listname, email])
            logMsg = listName + ": " + ret
	    next
        except subprocess.CalledProcessError:
            logMsg = "Error while trying to subscribe %s to %s\n" % (email, listName);
            logMsg += ret;
            
    elif(cmdVerb == "unsubscribe"):
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
		result = subprocess.check_output(cmd1.split(" "), preexec_fn=demote(user_uid, user_gid))
                logMsg = "Unsubscribed %s from %s" % (email, ln)
		next
	    except subprocess.CalledProcessError:
                logMsg = "Error while trying to unsubscribe %s from %s\n" % (email, ln);
                logMsg += "%s \n" % result 
        
            writeLog(LOG_FILE, logMsg);
    
    ### End of processCmd
    
def demote(user_uid, user_gid):
   def result():
     os.setgid(user_gid)
     os.setuid(user_uid)
   return result
    
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
        processCmd(cmd)
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
        processCmd(cmd);
        flgUnsub = 0;

