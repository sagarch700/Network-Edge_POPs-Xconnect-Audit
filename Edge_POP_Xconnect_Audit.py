""" Audit of organisations's xconnect id's & customer ckt id's(xconnect raised by partners/customers) for each edge POP location's
This will find the inconsistencies b/w the router description of xconnect and colo/data center xconnect db.
This will ensure that we are not paying MRC(monthly recurring charges) for something that we don't need
or something we are not tracking properly, we can either disconnect that xconnect or put them to use for
A bar graph is also made showing the xconnect ID's as per the EDGE POP routers, Customer
Ckt ID's per POP & xconnect ID's as per each POP location's database we get from colo/data centers.
"""

import csv
from napalm import get_network_driver
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import getpass


# Lists to the get the total number of xconnect ID's on POP routers, Customer Ckt ID's, and xconnect ID's as per POP colo databse
no_of_xconnect_id = list()
no_of_customer_ckt_id = list()
no_of_xconnect_id_db = list()
POP_location = list()
username = input("Username: ")
password = getpass.getpass()

# Getting the POP location details and their coresspondong router's ip addresses
# .txt file format should be Location:ip of r1:ip of r2 and so on
with open('LocationIP_1', 'r') as f:
    r = f.read().splitlines()
location_ip_list = list()
for items in r:
    location_ip_list.append(items.split(":"))

# Loop for each POP location
for a in location_ip_list:
    POP_location.append(a[0])
    differences_db_device = set()
    differences_device_db = set()

    # Dictionary for stroing xconnect ID and customer ckt ID data from edge POP routers with key as ID's and valus as interface no
    xconnect_id_dict = {}
    customer_ckt_id_dict = {}
    # Loop for each router in an edge POP location, one can have n number of routers in their edge POP locations
    for b in range(1, len(a)):
        ip = a[b]
        # Using Napalm module to ssh to cisco ios devices and getting relevant details, use iosxr in place of ios for xr device
        driver = get_network_driver('ios')
        # Passing arguments which includes username and password for ssh login
        ios = driver(ip, username=username, password=password)
        # Opening ssh session 
        ios.open()
        # get_interfaces output is a dictionary with key as interface number and value as attributes coressponding to that interface
        interface_output = ios.get_interfaces()
        hostname = ios.get_facts()['hostname']

        for x, y in interface_output.items():
            # Ignoring any loopback, Bundle, and sub interface types.
            if "Loopback" in x or "." in x or "Bundle-Ether" in x:
                continue
            # Storing values in xconnect_id_dict if interface description has XC_ID in them 
            elif "XC_ID" in y["description"]:
                xconnect_id = y["description"].split("#")[-2]
                xconnect_id_dict[xconnect_id] = f"{hostname} - {x}"
            # Storing values in xconnect_id_dict if interface description has CUST_ID in them
            elif "CUST_ID" in y["description"]:
                customer_id = y["description"].split("#")[-2]
                customer_ckt_id_dict[customer_id] = f"{hostname} - {x}"
        # Closing ssh session     
        ios.close()
    
    # Reading the xconnect inventory excel sheet that we get from edge POP location colo/data centers
    dataframe = pd.read_excel(f"{a[0]}_inventory.xlsx")
    # Converting the dataframe which has xconnect ID's  to list
    xconnect_id_db_list = dataframe["Sales Order Number"].tolist()
    # Storing the xconnect id's that we got from routers in a dictionary to the list
    xconnect_id_list = list(xconnect_id_dict.keys())

    # Storing the no of xconnect id's from routers, customer ckt id's from routers and xconnect id's from the colo database of each POP location to a list
    no_of_xconnect_id.append(len(xconnect_id_dict))
    no_of_customer_ckt_id.append(len(customer_ckt_id_dict))
    no_of_xconnect_id_db.append(len(xconnect_id_db_list))

    now = datetime.now()
    year, month, day = now.year, now.month, now.day

    # Finding out the inconsistencies b/w the xconnect ID's that we got from edge POP routers to the xconnect ID's from colo/data center db
    differences_device_db = set(xconnect_id_list) - set(xconnect_id_db_list)
    if differences_device_db:
        # writing those inconsistencies to a text file
        with open(f"inconsistencies_{year}-{month}-{day}.txt", 'w') as file:
            for x in differences_device_db:
                file.writelines(f"Present on Router, but not in xconnect db, xconnect-id: {x} and Router hostname & port: {xconnect_id_dict[x]} \n")
    # Finding out the discrepancies b/w the xconnect ID's that we got from colo/data center db to the xconnect ID's from edge POP routers
    differences_db_device = set(xconnect_id_db_list) - set(xconnect_id_list)
    if differences_db_device:
        # writing those inconsistencies to a text file
        with open(f"inconsistencies_{year}-{month}-{day}.txt", 'a') as file:
            for x in differences_db_device:
                file.writelines(f"Present in xconnect db, but not on router, xconnect-id: {x}, POP Location: {a[0]} \n")


# Plotting the bar graphs of Xconnect ID's as per the edge POP routers output, xconnect id's as per the colo/data center db &
#customer ckt ID's as per the edge POP routers output for each POP location 
labels = POP_location
x = np.arange(len(labels))
y1 = no_of_xconnect_id
y2 = no_of_xconnect_id_db
y3 = no_of_customer_ckt_id
width = 0.2
fig, ax = plt.subplots()
rects1 = ax.bar(x - width, y1, width, label = "Xconnect ID's")
rects2 = ax.bar(x, y2, width, label = "Xconnect ID's DB")
rects3 = ax.bar(x + width, y3, width, label = "Customer ckt ID's")

ax.set_ylabel("Xconnect ID's & Customer ckt ID's")
ax.set_title("Xconnect & Customer ckt ID's for each POP location")
ax.set_xticks(x, labels)
ax.set_xlabel("POP Locations")
ax.legend()

ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)
fig.get_tight_layout()
plt.savefig("edge pop inventory.png")