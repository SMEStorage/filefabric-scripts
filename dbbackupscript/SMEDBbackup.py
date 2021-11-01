# Copyright 2021 Vehera Ltd. trading as Storage Made Easy

# The information in this document is provided on an as-is basis. You use it at your own risk. 
# Storage Made Easy accepts no responsibility for errors or omissions, nor do we have any obligation to provide support for implementing or maintaining 
# the backup script and procedure described here. 
# Furthermore, we do not warrant that the design presented here is appropriate for your requirements.

import subprocess
import commands
import time
import logging
import smtplib
import argparse
import os
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


dbName = "smestorage"
keepDays = 14
backupDir = '/root/dbBackups/'

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help="Output Directory (default to /root/dbBackups)", default=backupDir)
parser.add_argument("-r", "--replicamode", help="Enable Replica backup mode")
args = parser.parse_args()


backupDir = args.output

if not ( backupDir.endswith("/") ):
	backupDir += "/"

if not (os.path.isdir(backupDir) ):
	print "Backup location is not valid"
	sys.exit(1)
	
#print(backupDir)
#print(args.replicamode)



logFile = "{0}{1}-backup.log".format(backupDir, time.strftime('%Y-%m-%d-%H%M'))
logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=logFile, level=logging.INFO, format=logFormat)


def serviceStatus(service):
	status = commands.getoutput("systemctl status " + service)
	if ("Active: active (running)" in status):
		return 1
	else:
		return 0

def stopstartService(action,service):
	count=0
	while count < 3:
		command = "systemctl", action, service
		subprocess.check_call(command)
		status = serviceStatus(service)
		if action == "stop" and status == 0:
			logging.info("Successfully Shutdown {0}".format(service))
			return 1
		if action == "start" and status == 1:
	                logging.info("Successfully Started {0}".format(service))
			return 1
		count+=1
	logging.error("Failed to {0} {1} ".format(action,service))
	return 0

def stopstartReplica(action):
	if (action == "stop"):
		command = 'mysql -e "STOP SLAVE;"'
		logging.info("Stop MariaDB Replication")
	else: 
		command = 'mysql -e "START SLAVE;"'
		logging.info("Restarting MariaDB Replicaton")
	logging.info(command)
	replicastatus = subprocess.Popen(command, shell=True,  stderr=subprocess.PIPE, stdout=subprocess.PIPE);
	stdout, stderr = replicastatus.communicate()
        exit_code = replicastatus.wait()
#	print(stdout, stderr, exit_code)
	time.sleep(10)
	return exit_code 
		
		

def backupMysql(location,db):
	command = '/bin/mysqldump {0} | gzip > {1}{2}-MySQLBackup.sql.gz'.format(db, location, time.strftime('%Y-%m-%d-%H%M'))
	logging.info("BackUp Started")
	logging.info(command)
	backup = subprocess.Popen(command, shell=True)
	backup.communicate()

def sendEmail():
	fromaddr = "#FROM EMAIL#"
	toaddr = ["#TO EMAIL1#", "#TO EMAIL2#"]
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ", ".join(toaddr)

	body = commands.getoutput("cat {0}".format(logFile))
	msg.attach(MIMEText(body, 'plain'))

	if ("ERROR" in body):
		logStatus = " - ERRORS occured"
	else:
		logStatus = " - SUCCESS"
	msg['Subject'] = "#CUSTOMER# DB Backup Logs {0}".format(logStatus)

	#For SSL instead of TLS replace server line with the line below, and comment server.starttls()
	#server = smtplib.SMTP_SSL('#mail.sslprovider.com#', 465)
	
	server = smtplib.SMTP('#smtp.gmail.com#', 587)
	server.starttls()
	server.login("#LOGIN#", "#PASSWORD#")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()


if (args.replicamode == "1"):
	stopReplica = stopstartReplica("stop")
	if not stopReplica:
		backupMysql(backupDir,dbName)
else: 
	stophttpd = stopstartService("stop","httpd")
	stopcrond = stopstartService("stop","crond")

	if stophttpd and stopcrond:
		backupMysql(backupDir,dbName)
	

logging.info("Purging backups older than {0} days".format(keepDays))
commands.getoutput("find {0} -type f -mtime +{1} -delete".format(backupDir, keepDays))

logging.info("Backups on Disk")
directoryListing = commands.getoutput("ls -lh {0}*.gz".format(backupDir))

for line in directoryListing.splitlines():
	logging.info(line)

if (args.replicamode == "1"):
	stopstartReplica("start")
else:
	stopstartService("start","httpd")
	stopstartService("start","crond")

sendEmail()

