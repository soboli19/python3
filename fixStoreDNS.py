#!/usr/bin/env python3
#This script will not work with python version below 3.6
import paramiko   # installed paramiko 2.6.0
import socket
import subprocess
import time
import sys
import os
import pymysql
sys.path.append("/home/users/isobolhj/public_html/esweb/includes") #this needs to be updated when script moved to rmps
from  passwordVaultRMPS import PasswordVault
from databaseMySQL import dbConnect
from ssh import RemoteConnection

# Checking if scrip executing manually with store(s) number as argument & input sanitation
for ar in sys.argv[1:] :
    if ar.isnumeric() and len(ar) == 5 :
        print("Processing input. Script will eliminate Help Center, Promise and SiteArch stores")
    else :
        print("One or more entered store numbers is not numeric or not 5 digits script can not cotinue.Use space as store number separator")
        sys.exit()

#Connetcing to rmps DB and building array with stores information where DNS need to be fixed
conn = dbConnect()
mycursor = conn.cursor()

if len(sys.argv) == 2:   #one store entered
    manualinput  = f"({sys.argv[1]})"
    select_manual = f"SELECT stnumber, environment, stcorename, stuser, stserver, stcentsrv, stinfraserver, stinfrauser FROM xxx WHERE ststoretype = 'R' AND visible_ind = 'Y' AND stinfraserver IS NOT NULL AND stnumber in {manualinput} AND stnumber NOT in (58601, 58603)"
    mycursor.execute(select_manual)
elif len(sys.argv) >= 2:
    manualinput = tuple(sys.argv[1:]) #multiple stores manually entered
    select_manual = f"SELECT stnumber, environment, stcorename, stuser, stserver, stcentsrv, stinfraserver, stinfrauser FROM xxx WHERE ststoretype = 'R' AND visible_ind = 'Y' AND stinfraserver IS NOT NULL AND stnumber in {manualinput} AND stnumber NOT in (58601, 58603)"
    mycursor.execute(select_manual)
else :
#Batch processsing - scanning all stores
    select_all = "SELECT stnumber, environment, stcorename, stuser, stserver, stcentsrv, stinfraserver, stinfrauser FROM xxx WHERE ststoretype = 'R' AND visible_ind = 'Y' AND stinfraserver IS NOT NULL AND stnumber NOT in (58601, 58603)"
    mycursor.execute(select_all)

sqlmyresult = mycursor.fetchall()
print("Fixing DNS for: ",len(sqlmyresult), " stores")
mycursor.close()
for s in sqlmyresult :
     print(s['stnumber'], " ", s['environment'], " ", s['stnumber'][:-2])

#Establishing ssh and executing bash commands remotely on ifrasrv. If connection can not be established or password missing/incorrect moving to another store
def live_connection(hostname, usr, command, infrasrv_status = True):
    scriptname = "RemoteConnection.py"
    mypassword = PasswordVault(usr, hostname, scriptname).getPassword()     
    if infrasrv_status:
#         if os.system("ping -c 1 " + hostname) is 0 :
        if os.system("ping -c 1 {} >/dev/null 2>/dev/null".format(hostname)) is 0 and mypassword.decode() != "ERROR - INVALID DATA OR SCRIPT ACCESS" :
            myssh = RemoteConnection(hostname, usr)
            connection = myssh.connect()
            _stdout,_stderr = myssh.execute(command)
            print(_stdout)
            myssh.close()
            srv_status = True
            return srv_status
        else:
            print("Server ", hostname, " is dead or having password issue")
            srv_status = False
            return srv_status
    else:
#         sys.exit("One of servers is not responding, script is not able to run")
        return None

#Using fuction live_connection  and executing bash commands remotely on ifrasrv and Rxserver. function fixStoreDNS use array as argument
def fixStoreDNS(storesArr):
     print("Fixing ", len(storesArr), " stores")
# Looping trough storelist array ssh to infrasrv and Rxserver, imported ssh module getting passwords from vault 
     for z in storesArr:
         STORE = z['stnumber']
         Rxserver = z['stserver']
         Infrasrv = z['stinfraserver']
         username = z['stuser'] 
         username1  = z['stinfrauser']
         st_env = z['environment']
#         print(st_env)
         if st_env.lower() == "sys1" :      #tstapp01
             APPSRV1_IP = "172.xxx.xxx.xxx"
             SBROKER_IP= "172.xxx.xxx.xxx"
         elif st_env.lower() == "sys2" :    #tstapp04
             APPSRV1_IP = "172.xxx.xxx.xxx"
             SBROKER_IP = "172.xxx.xxx.xxx"
         elif st_env.lower() == "prodfix" : #tstapp02 ProdFix
             APPSRV1_IP = "172.xxx.xxx.xxx"
             SBROKER_IP="172.xxx.xxx.xxx"
         elif st_env.lower()[:-1] == 'dev' :        #Rx DEV store st_env.lower()[:-1] == 'dev' another option 
             APPSRV1_IP="172.xxx.xxx.xxx"
             SBROKER_IP="172.xxx.xxx.xxx" 
         else :
             break
# Building dns update commands and store them in files on store /tmp 
         command1 = f"""server infrasrv
zone {STORE}.store.walgreens.com
update delete appsrv1.{STORE}.store.walgreens.com
show
send

update add appsrv1.{STORE}.store.walgreens.com 172800 A {APPSRV1_IP}
show
send

zone {STORE}.store.walgreens.com
update delete SBroker.{STORE}.store.walgreens.com
show
send

update add SBroker.{STORE}.store.walgreens.com 172800 A {SBROKER_IP}
show
send
         """
#         print("check for 4 digit store", "\n", command1)
         command2 = f'echo "{command1}" > /tmp/nsupdate_dnsfix_script; cat /tmp/nsupdate_dnsfix_script|nsupdate'
         command3 = f"""server infrasrv
update delete pepsf5b.{STORE}.store.walgreens.com A
update delete tandem_backup.{STORE}.store.walgreens.com CNAME
update add depsf5wag2b.{STORE}.store.walgreens.com 86400 A 172.xxx.xxx.xxx
update add tandem_backup.{STORE}.store.walgreens.com 86400 CNAME depsf5wag2b.{STORE}.store.walgreens.com
update delete pepsf5p.{STORE}.store.walgreens.com A
update delete tandem_primary.{STORE}.store.walgreens.com CNAME
update add depsf5wag2p.{STORE}.store.walgreens.com 86400 A 172.xxx.xxx.xxx
update add tandem_primary.{STORE}.store.walgreens.com 86400 CNAME depsf5wag2p.{STORE}.store.walgreens.com
show
send
         """
         command4 = f'echo "{command3}" > /tmp/tandem_dnsfix_script; cat /tmp/tandem_dnsfix_script|nsupdate'
         command5 = f"{command2}; {command4}"

# Bilding commands for updating infrasrv DNS configuration files
         command6 = """if [ $(cat /etc/resolv.conf | grep -e 172.31.73.252 -e 172.31.73.253 | wc -l) -eq 2 ]; then echo 'resolv.conf is good'; else echo 'Fixing resolv.conf'; sed -i.bkp 's/172\.28\.41\.161/172.31.73.252/g;s/172\.28\.41\.165/172.31.73.253/g' /etc/resolv.conf ; fi;
cp /etc/named.d/forwarders.conf /etc/named.d/forwarders.conf-orig;
 echo 'forwarders { 172.xxx.xxx.xxx; 172.xxx.xxx.xxx; };'>/etc/named.d/forwarders.conf;
if [ $(cat /etc/named.conf |grep allow-query | wc -w) -lt 17 ]; then echo 'some entries in allow-query missing fixing problem'; sed -i.bkp 's/172.xxx.xxx.xxx;/& 172.xxx.xxx.xxx; 172.xxx.xxx.xxx; 10.0.0.0\/8; 172.0.0.0\/8; /' /etc/named.conf; else echo 'allow-query is good'; fi;
if [ $(cat /etc/named.conf |grep allow-recursion | wc -w) -lt 8 ]; then echo 'some entries in allow-recursion missing fixing problem'; sed -i '11 s/192.168.0.0\/16;/& 10.0.0.0\/8; 172.0.0.0\/8; /' /etc/named.conf; else echo 'allow-recursion is good'; fi; if [ $(cat /etc/named.conf |awk '/allow-update { 172.21.225.144/{print}'| awk 'FNR==3 {print}'| wc -w) -lt 7 ]; """
         
         command61 = f"""then echo '{STORE}.store.walgreens.com missing entries. Fixing problem'; sed -i '/{STORE}.store.walgreens.com/"""
         
         command63 = """ {n; n; n; n; n; s/localhost;/ localhost; 10.0.0.0\/8; 172.0.0.0\/8;/; }' /etc/named.conf; else echo '{STORE}.store.walgreens.com looks good'; fi;
cd /var/lib/named/master;  for x in $(grep -m1 it-sxmp *|awk -F: '{print$1}'); do sed -i.bkp 's/it-sxmp-4dns/dlw2nii-dns01/g;s/it-sxmp-5dns/dlw2nii-dns02/g' $x; if [[ -f $x.jnl ]]; then rm $x.jnl; fi; done; sed -i.bkp 's/png2yp02\.store/dlw2nii-dns01/g;s/png2yp03\.store/dlw2nii-dns02/g'"""
         command64 = f""" {STORE}.store.walgreens.com; echo 'Primary and Secondary subnets fixed';
service named restart
         """
         command7 = f"{command6}{command61}{command63}{command64}"
         print(command7)
         print("Connecting and fixing ", "store:", STORE, " ",Infrasrv)
         infra_status = live_connection(Infrasrv, username1, command7) # infra_status parameter passed to Rxserver to skip if infrasrv is not responding command7
         if infra_status:
             print("Connecting and fixing ", Rxserver)
             live_connection(Rxserver, username, command5, infra_status) # command5 
         else:
             print("skipping ", Rxserver, " dns commands infrasrv not responding ", STORE, " DNS not fixed") 

fixStoreDNS(sqlmyresult)

