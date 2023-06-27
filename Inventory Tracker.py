#Analyzes the product export csv from Shopify to determine
#which packets have a zero inventory, and
#which bulk items need to be reallocated

import re
import csv

#two lists of product skus for packets/bulk that are not active and should thus be excluded from the inventory analysis
not_active_pkts = ['CRA-SB-pkt', 'FLO-BO-pkt', 'MAL-PL-pkt', 'STA-RU-pkt', 'LET-MM-pkt'\
              'SOY-WL-pkt', 'GAR-HP-pkt', 'PER-OS-pkt', 'SNA-AG-pkt']
not_active_bulk = ['PEA-CA-5lb']

#establishing empty lists and an iterator to be used below
packets=[]
bulk=[]
bulk_zero_inv=[]
i=0

#opening the 'product_export' csv file
with open("product_export.csv","r", encoding='utf-8') as export_file:
    reader=csv.reader(export_file)
    #skips header row
    header=next(reader)
    for row in reader:
        #checks to see if the inventory quantity is even being tracked
        if row[16] == 'shopify':
            #pulls packet items
            if 'pkt' in row[14]:
                #checks to see if the inventory quantity is low (less than 25)
                if row[14] not in not_active_pkts:
                    if int(row[17]) <= 25 and int(row[17]) >= 0:
                        #extracts portion of string between single quotes (aka the variety name)
                        try:
                            t=re.findall(r"'(.+?)'", row[1])[0]
                            packets.append([t,int(row[17])])
                        except:
                            packets.append([row[1],int(row[17])])
            #pulls bulk, misc items
            else:
                #filters out misc garbage
                if row[14] == "":
                    continue
                else:
                    bulk.append([row[14],int(row[17]),row[9],row[0]])

#This section generates the report csv file     
with open("product_report.csv", "w", newline='') as report_file:
    writer=csv.writer(report_file)
    writer.writerow(["LOW INVENTORY (PACKETS)"])
    #writes the low inventory packets
    for x in packets:
        writer.writerow(x)

    writer.writerow("")
    writer.writerow(["BULK QTYS TO DIVVY UP"])

    #this sections examines the list of bulk items and records sold out items
    #it also examines each variety to check if any bulk sizes need to be reallocated
    #due one or more of the smaller sizes being sold out
    a,b,c,d,e,v,w,x,y,z="","","","","",0,0,0,0,0
    for row in bulk:
        row_writer = False
        #appends bulk zero inventory with sku if qty=0
        if row[0] not in not_active_bulk:
            if row[1]==0:
                #checking the first char of the bulk size to filter out non-seed items
                if row[2][0].isdigit():
                    bulk_zero_inv.append(row[3])

        #checks to see if any bulk sizes need to be reallocated
        #this if statement will skip over non-seed items            
        if row[0][:6] == "MER-GT" or row[0][:6] == "TOO-OP":
            continue
        elif a == "":
            a,v=row[0][:6],row[1]
        elif b == "":
            b,w=row[0][:6],row[1]
            if a == b:
                continue
            else:
                a,v=b,w
                b,w="",0
        elif c == "":
            c,x=row[0][:6],row[1]
            if c == b:
                continue
            else:
                if v == 0 and w > v:
                    writer.writerow([a])
                    row_writer = True
                a,v = c,x
                b,c,w,x="","",0,0
        elif d == "":
            d,y=row[0][:6],row[1]
            if d == c:
                continue
            else:
                if ((v == 0 and (w > v or x > v)) or
                    (w == 0 and (x > w))):
                    writer.writerow([a])
                    row_writer = True
                a,v=d,y
                b,c,d,w,x,y="","","",0,0,0
        elif e == "":
            e,z=row[0][:6],row[1]
            if e == d:
                continue
            else:
                if ((v == 0 and (w > v or x > v or y > v)) or 
                    (w == 0 and (x > w or y > w)) or
                    (x == 0 and (y > x))):
                    writer.writerow([a])
                    row_writer = True
                a,v=e,z
                b,c,d,e,w,x,y,z="","","","",0,0,0,0
        else:
            continue
        
    writer.writerow("")
    writer.writerow(["BULK ZERO INVENTORY"])
    #writing out bulk items that have zero inventory regardless of what size they are
    for item in bulk_zero_inv:
        writer.writerow([item])
        
