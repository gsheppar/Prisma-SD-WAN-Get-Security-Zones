#!/usr/bin/env python
##############################################################################
# Import Libraries
##############################################################################
import prisma_sase
import argparse
import sys
import csv
from csv import DictReader
##############################################################################
# Prisma SD-WAN Auth Token
##############################################################################
try:
    from prismasase_settings import PRISMASASE_CLIENT_ID, PRISMASASE_CLIENT_SECRET, PRISMASASE_TSG_ID

except ImportError:
    PRISMASASE_CLIENT_ID=None
    PRISMASASE_CLIENT_SECRET=None
    PRISMASASE_TSG_ID=None


def report(sase_session):
    zone_id2n = {}
    for zone in sase_session.get.securityzones().cgx_content['items']:
        zone_id2n[zone["id"]] = zone["name"]
        #print(zone["name"] + "  " + zone["id"])
    
    interface_list = []      
    for site in sase_session.get.sites().cgx_content['items']:
        print("Checking site " + site["name"])
        for element in sase_session.get.elements().cgx_content['items']:
            if element["site_id"] == site["id"]:
                print("Checking element " + element["name"])
                for interface in sase_session.get.interfaces(site_id = site["id"], element_id = element["id"]).cgx_content['items']:
                    #print("Checking interface " + interface["name"])
                    data = {}
                    data["site_name"] = site["name"]
                    data["element_name"] = element["name"]
                    data["interface_name"] = interface["name"]
                    data["used_for"] = interface["used_for"]
                    data["security_zone"] = ""
                    
                    for zone in sase_session.get.elementsecurityzones(site_id = site["id"], element_id = element["id"]).cgx_content['items']:
                        if zone["interface_ids"]:
                            if interface["id"] in zone["interface_ids"]:
                                #print(zone["id"])
                                #print(zone_id2n)
                                try:
                                    data["security_zone"] = zone_id2n[zone["zone_id"]]
                                except Exception as e:
                                    print('Failed')
                                    print(zone)
                                    data["security_zone"] = zone["zone_id"]
                                    return
                                    
                        if zone["waninterface_ids"]:
                            if interface["id"] in zone["waninterface_ids"]:
                                #print(zone["id"])
                                #print(zone_id2n)
                                try:
                                    data["security_zone"] = zone_id2n[zone["zone_id"]]
                                except Exception as e:
                                    print('Failed')
                                    print(zone)
                                    data["security_zone"] = zone["zone_id"]
                                    return
                            
                    
                    
                    interface_list.append(data)
    
    csv_columns = []        
    for key in interface_list[0]:
        csv_columns.append(key)
    
    csv_file = "report.csv"
    with open(csv_file, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in interface_list:
            try:
                writer.writerow(data)
            except:
                print("Failed to write data for row")
        print("Saved " + csv_file + " file")
    
    return

def go():

    ##############################################################################
    # Login
    ##############################################################################
    sase_session = prisma_sase.API()
    
    sase_session.interactive.login_secret(client_id=PRISMASASE_CLIENT_ID,
                                          client_secret=PRISMASASE_CLIENT_SECRET,
                                          tsg_id=PRISMASASE_TSG_ID)
    if sase_session.tenant_id is None:
        print("ERR: Login Failure. Please provide a valid Service Account")
        sys.exit()
    
    report(sase_session)
   

    return

if __name__ == "__main__":
    go()