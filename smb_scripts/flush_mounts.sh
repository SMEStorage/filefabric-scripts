#!/bin/bash

############################################
##   script name: flush_mounts.sh         ##
##   version: 1.1                         ##
##   author: eric@storagemadeeasy.com     ##
##   puropse: This is a shell script      ##
##           which is designed to allow   ##
##           sme customers to umount      ##
##           any cifs shares of a         ##
##           specific filer.              ##
##                                        ##
############################################
nas="0"
user="0"
confirm="n"

# write out log files to the location below
logf="/var/log/sme_flushmount.log"

# Use Iso8601 time standard to the second for log files
datecmd="date -Iseconds"

# program will accept two arguments: -n and -h
#	-n is required and is the name of the nas on which you are looking to flush mounts
#	-h is used for help command to show the arguments needed
while getopts "n:u:h" opt; do
	case ${opt} in
	n) nas=$OPTARG
	;;
	u) user=$OPTARG
	;;
	h)
		echo "Script to unmount existing CIFS shares on the SME System"
		echo -e "-n <nas name> \t\t\t -- The name of the nas you are looking to umount existing shares on"
		echo -e "-u <username to umount> \t -- The name of the user you are looking to umount existing shares on"
		exit 1
	;;
	\? )
		echo "Usage: $0 -n <nas name> -u <username> "
		exit 1
	;;
	: )
		echo "Invalid Option: -$OPTARG requires an argument" 1>&2
		exit 1
	;;
	esac
done

	if [ ${nas} ==  "0" ] && [  ${user} == "0" ]; then
		# in case the user doesn't specify a nas location, we will alert them and exit
		echo "Please enter your NAS device's name or Username"
		exit 0
	fi

	# For the users and our logs we will grab the list of all the shares mounted for that nas device, as well as the mount paths for those shares
	if [ ${nas} != "0" ] &&  [ ${user} != "0" ]; then
    		mounts=`mount | grep -ie "//${nas}" -ie '\\\\'${nas}| grep -i cifs | grep -i username\=${user} | sed s/.*on\ //g | sed s/\ type.*//g | sort | uniq`
    		shares=`mount | grep -ie "//${nas}" -ie '\\\\'${nas} | grep -i cifs | grep -i username\=${user} |  awk '{split($6,s,","); print s[5] " @ " $1 " ; "}'` 
	fi

	if [ ${nas} != "0" ] && [ ${user} == "0" ]; then
    		mounts=`mount | grep -ie "//${nas}" -ie '\\\\'${nas}| grep -i cifs | sed s/.*on\ //g | sed s/\ type.*//g | sort | uniq`
    		shares=`mount | grep -ie "//${nas}" -ie '\\\\'${nas} | grep -i cifs |  awk '{split($6,s,","); print s[5] " @ " $1 " ; "}'`
	fi

	if [ ${user} != "0" ] && [ ${nas} == "0" ]; then
    		mounts=`mount | grep -i cifs |  grep -i username\=${user} | sed s/.*on\ //g | sed s/\ type.*//g | sort | uniq`
    		shares=`mount | grep -i cifs |  grep -i username\=${user}  | awk '{split($6,s,","); print s[5] " @ " $1 " ; "}'`
	
	fi


	# Prompt the user to make share the shares associated with this nas are in fact the ones they want to umount
	echo "Umount the following CIFS mounts:"
	echo $shares
	echo "[y/n]"
	read confirm
	

	if [ ${confirm} == "y" ]; then
		# the users enter's yes, so we will log what shares are attempting to be unmounted, run the unmount and the log each of the mount paths we unmounted
		echo `$datecmd` " - Umounting $shares" | tr '\n' ' ' >> $logf
		echo " " >> $logf

		for i in $mounts; do umount $i; done
		mount_status=$?

		echo `$datecmd` " - The following mount locations have been flushed: $mounts" | tr '\n' ' ' >>$logf 
		echo " " >> $logf

		echo `$datecmd` " - Mount command status: $mount_status" >> $logf
	
	elif [ ${confirm} == "n" ]; then
		# user decides these aren't the shares they want to unmount, so we exit and do nothing
		echo `$datecmd` " - Opted not to unmount $shares" | tr '\n' ' ' >> $logf
		echo " " >> $logf
		exit 
	else
		# user enters something other than y or n, so lets just be safe and exit
		echo 'Please enter "y" or "n"'
		exit
	fi

