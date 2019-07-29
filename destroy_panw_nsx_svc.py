#!/usr/bin/python

#Program:        destroy_panw_nsx_svc.py
#Description:    Destroys Palo Alto Networks NSX Service
# This python2.7 script makes API calls to NSX manager to remove orphaned
# Panorama objects that didn't get removed during service removal.
# Use only if you removed the NSX configuration from Panorama, but the
# objects were not removed from NSX Manager.
#Version:        1.0
#Date:           05/22/2019, updated 07/03/2019
#Lead Developer: Jack Parks


import requests
import urllib3
import xml.etree.ElementTree as ET
import argparse
urllib3.disable_warnings()

def getPaloSvcMgr():
    '''
    This function fetches Service Manager object by identifying the user __vmware_nsx.
    After locating this username, the script finds the service manager object id,
    and the service object id
    '''

    urlSvcMgrAPI="/api/2.0/si/servicemanagers"

    try:
           response = requests.get(baseURL+urlSvcMgrAPI, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
           print "Connection error!"

    '''Make a Backup copy of the XML in the script directory'''
    with open('nsxservicemanagers.xml', 'wb') as f:
        f.write(response.content)

    xmlFile = "nsxservicemanagers.xml"

    xmlString = ET.parse(xmlFile)

    root = xmlString.getroot()

    '''Loop through the XML to get the relevant information we need'''
    for svcMgr in root.findall('./serviceManager'):

        for login in svcMgr.findall('login'):

            if login.text == '__vmware_nsx':
                print "Found Palo Alto Networks NSX username:  ", login.text
                print "------------------------------------------"

                for mgrName in svcMgr.iterfind('name'):
                    print "Found the Service Manager Name of:  ", mgrName.text


                for objID in svcMgr.iterfind('objectId'):
                    print "Found the Service Manager ID:  ", objID.text

                for svcObjID in svcMgr.iterfind('services/basicinfo/objectId'):
                    print "The Service ID is:  ", svcObjID.text

            return mgrName.text, objID.text, svcObjID.text

    #print response.text
    '''Store Service Manager ID as variable, store service object ID as variable -  pass to def getPaloService()'''

def getPaloService(serviceObj):

    '''
    This function uses the service object id to find the service instances object id
    '''

    urlSvcAPI="/api/2.0/si/services"

    try:
        response = requests.get(baseURL+urlSvcAPI, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
        print "Connection error!"

    with open('nsxservices.xml', 'wb') as f:
        f.write(response.content)

    xmlFile = "nsxservices.xml"

    xmlString = ET.parse(xmlFile)

    root = xmlString.getroot()

    '''Loop through the XML to get the relevant information we need'''
    for listSvc in root.findall('./service'):

        for objID in listSvc.iterfind('objectId'):

            if objID.text == serviceObj:
                print "Checking Service Object Attributes for:  ", objID.text
                print "------------------------------------------"

                for svcInst in listSvc.iterfind('serviceAttributes/attribute/value'):

                       if svcInst.text is not None and "serviceinstance" in svcInst.text:

                           print "Found the Service Instance:  ", svcInst.text
                           break

                for svcName in listSvc.iterfind('name'):
                    print "Found Service Instance Name:  ", svcName.text


                return svcName.text, svcInst.text


def getPaloSvcProfile(serviceID):

    '''
    This function uses the service object id to find all of the service profiles.
    There will be a service profile for every Zone created under Panorama for the
    NSX service.
    '''
    urlSvcProfileAPI="/api/2.0/si/serviceprofiles"

    try:
            response = requests.get(baseURL+urlSvcProfileAPI, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
            print "Connection error!"

    with open('nsxserviceprofiles.xml', 'wb') as f:
        f.write(response.content)

    xmlFile = "nsxserviceprofiles.xml"

    xmlString = ET.parse(xmlFile)

    root = xmlString.getroot()

    profObjIDs = []
    print "Checking Service Profiles for:  ", serviceID
    print "------------------------------------------"

    '''Loop through the XML to get the relevant information we need'''
    for listSvcProf in root.findall('./serviceProfile'):

        for prof1ObjID in listSvcProf.iterfind('objectId'):

            for objID in listSvcProf.iterfind('service/objectId'):

                if objID.text == serviceID:

                    for profObjID in listSvcProf.iterfind('objectId'):
                        print "Found Service Profile ID:  ", profObjID.text

                    for profName in listSvcProf.iterfind('name'):
                        print "It has the name of:  ", profName.text
                        print " "

                    profObjIDs.append(profObjID.text)
            #print profObjIDs
        return profObjIDs

def destroySvcProfiles(profile):
    '''
    This function deletes the service profiles (aka zones).
    '''

    urlDelSvcProfAPI="/api/2.0/si/serviceprofile/"

    try:
            r1 = requests.delete(baseURL+urlDelSvcProfAPI+profile, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
            print "Connection error!"

    print r1.status_code

def destroyService(instance, service, manager):

    '''
    This function deletes the service instance, service, and the service manager.
    '''

    urlDelSvcInstAPI="/api/2.0/si/serviceinstance/"
    urlDelSvcAPI="/api/2.0/si/service/"
    urlDelSvcMgrAPI="/api/2.0/si/servicemanager/"

    try:
            r1 = requests.delete(baseURL+urlDelSvcInstAPI+instance, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
            print "Connection error!"

    try:
            r2 = requests.delete(baseURL+urlDelSvcAPI+service, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
            print "Connection error!"

    try:
            r3 = requests.delete(baseURL+urlDelSvcMgrAPI+manager, headers=nsx_headers,auth=(nsxmanager_user,nsxmanager_password), verify=False)
    except requests.exceptions.ConnectionError as e:
            print "Connection error!"

    print r1.status_code
    print r2.status_code
    print r3.status_code

def main():
    global baseURL
    global nsxmanager_user
    global nsxmanager_password
    global nsx_headers

    print " "
    print "------------------------------------------"
    print " "
    print "This python2.7 script makes API calls to NSX manager to remove orphaned "
    print "Panorama objects that didn't get removed during service removal."
    print "Use only if you removed the NSX configuration from Panorama, but the "
    print "objects were not removed from NSX Manager."
    print " "
    print "!!! USE AT YOUR OWN RISK !!!"
    print " "
    print "------------------------------------------"
    print " "

    baseURLinput = raw_input("Enter IP or Hostname of NSX Manager: ")
    baseURL = "https://"+baseURLinput
    nsxmanager_user = raw_input("Enter NSX Manager Admin username: ")
    nsxmanager_password = raw_input("Enter NSX Manager Admin password: ")

    nsx_headers={'content-type':'application/xml'}
    nsxService = []
    nsxSvcInst = []
    nsxSvcPro = []

    '''Call the Function to get the service manager & service ids'''
    nsxService = getPaloSvcMgr()
    print " "

    '''Call the function to get the service instance id'''
    nsxSvcInst = getPaloService(nsxService[2])
    print " "

    '''Call the function to get the service profiles (aka zones)'''
    nsxSvcPro = getPaloSvcProfile(nsxService[2])
    print " "
    print "------------------------------------------"
    print " "
    print "This Script is about to remove your Panorama configuration from NSX manager"
    print "This is permanent!!!"
    print " "
    print "------------------------------------------"

    finalAnswer = raw_input("Type DELETE to confirm:  ")

    if finalAnswer == "DELETE":
      print "....Destroying Panorama NSX Service...."

      svcProLen = len(nsxSvcPro)
      for i in range(0, svcProLen):
        print "Deleting " + nsxSvcPro[i]
        destroySvcProfiles(nsxSvcPro[i])

      print "Deleting " + nsxSvcInst[1]
      print "Deleting " + nsxService[2]
      print "Deleting " + nsxService[1]
      destroyService(nsxSvcInst[1], nsxService[2], nsxService[1])

    else:
      print "....Aborting...."



if __name__ == "__main__":

    # calling main function
    main()
