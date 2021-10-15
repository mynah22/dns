from os import system, getlogin
from time import localtime, sleep
from subprocess import check_output, DEVNULL
import re
ippattern= re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

targetMachine = input("enter target host: \n")
username = input("enter username: \n")
me=getlogin()

validIP=False
while not validIP:
    rightIP = input("enter correct IP: \n")
    if ippattern.search(rightIP):
        validIP=True
    else:
        print("Invalid IP. ")
system('cls')

firstrun=True
trackedIPs=[]

def currentTime():
    return str(localtime()[3])+':'+str(localtime()[4]).zfill(2)

def determinePinging(targetIP):
    global pinging
    if str(check_output("ping -n 1 "+targetIP)).count('TTL'):
        for knownIP in trackedIPs:
            if knownIP['Address'] == targetIP:
                knownIP['LastPinged'] = currentTime()
        return True,None
    else:
        for knownIP in trackedIPs:
            if knownIP['Address'] == targetIP:  
                lastping=knownIP['LastPinged']
        return False, lastping

def determineNSResolution():
    global currentResolution
    addresses =[]
    for line in check_output("nslookup "+targetMachine, stderr=DEVNULL).splitlines()[4:]:
        try:
            addresses.append(ippattern.search(str(line))[0])
        except:
            pass
        for justSeenIP in addresses:
            unique=True
            for knownIP in trackedIPs:
                if knownIP['Address'] == justSeenIP:
                    knownIP['LastResolved'] = currentTime()
                    unique=False
            if unique:
                trackedIPs.append({'Address':justSeenIP, 'LastResolved':currentTime(), 'LastPinged':'never'})
    currentResolution = (addresses)

status=('firstrun',currentTime())
def statusUpdate(newStatus):
    global status
    if newStatus != status[0]:
        system("title = "+targetMachine+"  "+username+"   "+newStatus)
        system("(((echo "+username+" at "+targetMachine+") & echo old status [since "+status[1]+"] "+status[0]+" ) & echo new status [since "+currentTime()+"] "+newStatus+") | msg "+me)
        status=(newStatus, currentTime())




#Begin Main loop

while True:
    if not firstrun:
        print('previously resolved IPs below. IPs are only ping-tested if they are currently resolved by nameserver.')
        for item in trackedIPs:
            print(item['Address']+'\n    last ping: '+item['LastPinged']+'\n    last dns:  '+item['LastResolved'])
        print('\n\n\nCURRENT RESULTS:')

    determineNSResolution()

    if len(currentResolution) == 0:
        print("hostname "+targetMachine+" is not resolving to any ip addresses")
        system("color 40")
        statusUpdate('NoForward')

    elif len(currentResolution) == 1:
        print("hostname "+targetMachine+" Resolving to "+currentResolution[0]+", pinging...\n")
        pingResults=determinePinging(currentResolution[0])
        if pingResults[0]:
            print(currentResolution[0]+" is pinging")
            if currentResolution[0]==rightIP:
                system("color 20")
                statusUpdate('pinging expected')
            else:
                if currentResolution.count(rightIP):
                    note0="resolving, "
                else:
                    note0="not resolving, "
                print("Pinging different ip than expected:\n    "+rightIP+"(expected, "+note0+"not pinging)\n    "+currentResolution[0]+"(currently resolving and pinging)")
                system("color 30")
                statusUpdate('pinging UNexpected')
        else:
            print(currentResolution[0]+" is NOT pinging. last successful ping was at "+pingResults[1])   
            system("color 40")
            statusUpdate('not pinging')

    elif len(currentResolution) > 1:
        pingingIPs=[]
        rightAddressPinging=False
        print("hostname "+targetMachine+" Resolving to multiple ips:\n")
        for ip in currentResolution:
            print("    "+ip)
        print('\n\n\nPing testing resolved IPs...\n')
        for ip in currentResolution:
            pingResults=determinePinging(ip)
            if pingResults[0]:
                print(ip+" is pinging")
                pingingIPs.append(ip)
            else:
                print(ip+" is NOT pinging. last successful ping was at "+pingResults[1])

        #screen color casing for instances with multiple resolved IPs that are pinging
        if pingingIPs == 0 :
            system("color 40")
            statusUpdate('not pinging multiple')
        elif pingingIPs == 1 :
            if rightAddressPinging: 
                system("color 20")
                statusUpdate('pinging expected, multiple resolved')
            else:
                system("color 30")
                print("Pinging different ip than expected:\n    (expected)"+rightIP+"\n    (currently resolving and pinging)"+currentResolution[0])
                statusUpdate('pinging UNexpected')
        elif pingingIPs > 1 :
            if pingingIPs.count(rightIP): 
                system("color 20")
                print("Pinging correct IP and unexpected IP(s). See above for details")
                statusUpdate('pinging expected, and other(s)')
            else:
                system("color 30")
                print("Pinging multiple unexpected IPs:\n    (expected)"+rightIP+"-  See above for details")
                statusUpdate('pinging multiple UNexpected')




    if firstrun:
        sleep(1)
    else:
        sleep(15)
    system('cls')
    firstrun=False