# Destroy-PAN-NSX-Objects
This python2.7 script is for removing orphaned Panorama NSX objects from NSX Manager

#Detail Description
There are instances when the Panorama NSX-V plug-in objects do not properly get removed from the NSX-V manager properly.  Attempts to remove these objects from within the vCenter Networking and Security configuration screen do not work.  The only way to clean up the leftover objects is to utilize the NSX manager’s API.  

This Python script dynamically and systematically identifies the orphaned Panorama objects and removes them from the NSX Manager via the API.  This script was written in Python 2.7 and requires the following libraries:
* requests
* urllib3
* ElementTree

This Python script will make the API calls to NSX Manager and download the XML to the folder that the script was executed from.  This provides a rudimentary back up of sort in case of errors.  The script user will be presented with the objects that the script has identified and wait for user confirmation before making the DELETE API calls to remove the objects.

This is script is provided for use in Lab and POC environments when orphaned Panorama objects need to be removed from NSX Manager.  Do not use in a production environment without extensive testing.

This script was developed using Python 2.7 on MacOS 10.14.  It has been tested on NSX Manager 6.4 (NSX-V).  The NSX objects were created using Panorama 8.1 & 9.0 with plugin 2.0.x

# Support Policy
The code and templates in the repo are released under an as-is, best effort, support policy. These scripts should be seen as community supported and Palo Alto Networks will contribute our expertise as and when possible. We do not provide technical support or help in using or troubleshooting the components of the project through our normal support options such as Palo Alto Networks support teams, or ASC (Authorized Support Centers) partners and backline support options. The underlying product used (the VM-Series firewall) by the scripts or templates are still supported, but the support is only for the product functionality and not for help in deploying or using the template or script itself. Unless explicitly tagged, all projects or work posted in our GitHub repository (at https://github.com/PaloAltoNetworks) or sites other than our official Downloads page on https://support.paloaltonetworks.com are provided under the best effort policy.
