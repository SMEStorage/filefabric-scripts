# Monitoring Tools

Nagios style plugins for monitoring the File Fabric Appliance

## Requirements

No additional requirements for the File Fabric appliance, will run as the ROOT user with default tools installed. 

Monitoring system is outside of the scope of these tools, can either be run via cli or pluged into any monitoring system that supports nagios-type checks. 

## Getting Started

The script files can be selectively downloaded via wget/curl into your File Fabric appliance, or the entire repo can be downloaded and scripts copied out as required. 

## Running

### sme_mariadb_repl_check

Accepts the follwoing flags:
    -w <number of seconds>   --- seconds behind Master for DB replication to issue a warning
    -c <number of seconds>   --- seconds behind Master for DB replication to issue a critical 
    -u <mariadb username>    --- if you are using a different user than the default SME db user
    -p <mariadb password>    --- if you are using a different password than the default SMB db user
    -h <host:port>           --- to issue the check command against a specific db instance, default is localhost

### check_sme_folder
    -e <host>                --- File Fabric instance you would like to do the API check for
    -u <username>            --- File Fabric User to use to Login 
    -p <password>            --- File Fabric Password for the user specified with the -u
    -f <folder name>         --- Full SME path to the folder you would like to validate

## License

[MIT](http://opensource.org/licenses/mit-license.php)
