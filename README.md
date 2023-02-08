# Network-Edge_POP-Xconnect-Audit
Xconnect audit of an organisation's edge POP locations that will ensure it is not paying for more than what is in use currently.  

# Pre-requisites
* Make an inventory file that has the edge POP locations and their corresponding router ip addresses in the format location:router-1 IP:router 2 IP:... and so on. for eg: 
  * Singapore:192.168.228.200:192.168.201\n
  * London: 192.168.228.202
* Make sure you have a proper naming convention on your interface description that can help the code in extracting the xconnect and customer id's. the  sample naming convention(starting with # and ending with #): 
  * #U or P or I or C#Protocol or Customer service#Customer name#Service order#XC_ID or CUST_ID#Xconnect ID no or Customer ckt ID#
     U: IP transit/upstream, P: Private peering, I: internet exchange, C: Customer, XC_ID: Xconnect raised by us, CUST_ID: Xconnect raised by the                customer/Partner.   
  
# Code tries to achieve/help with the below points.
Code reuturns a bar graph and a inconsistencies.txt file that will help in below analysis.

* Going through the inconsistencies file, the organisation can further investigate  for the inconsistencies b/w the xconnect ID's configured on the           routers and the xconnect id's as per the colo/data center database.
* The bar graph and inconsistencies file will help an organisation to check whether they are paying for the xconnects that are not in use currently or that   were meant to be disconnected, this will save a lot of MRC(monthly recurring charges) per xconnect.
* From the bar graph comparing the no of xconnect id's and customer ckt id' an organisation can leverage this information to negotiate with the future       customers/partners requesting them to raise xconnects if an organisation has raised considerable amount of xconnects when compared to the xconnects         raised by their existing customer/partners at a certian POP location, saving any extra NRC/MRC.
