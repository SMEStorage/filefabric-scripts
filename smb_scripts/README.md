# SMB Scripts

Support scripts for the Enterprise File Fabric related to the SMB connector

## Requirements

No additional requirements for the File Fabric appliance, will run as the ROOT user with default tools installed

## Getting Started

The script files can be selectively downloaded via wget/curl into your File Fabric appliance, or the entire repo can be downloaded and scripts copied out as required. 

## Running

### Flush Mounts

Can be run per appliance with a -n for the name or ip of the nas you look to clear out stale mounts:

./flush_mounts.sh -n <NAS_name_or_IP_address>

## License

[MIT](http://opensource.org/licenses/mit-license.php)
