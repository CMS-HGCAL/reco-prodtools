#! /usr/bin/env python
import os
import sys
import commands
import time

def processCmd(cmd, quite = 0):
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

# default is pt 35 photon, although currently require new arguments
PDGid='22'
PT='35'

if len(sys.argv) == 3:
    PDGid = str(sys.argv[1])
    PT = str(sys.argv[2])
else: sys.exit( "Wrong number of arguments: require 1. the PDGid and 2. the pT" )

print "about to submit GSD jobs"
print "PDGid = ",PDGid
print "PT = ",PT
os.system('./edSubmitGunImproved.sh GSD '+PDGid+' '+PT)

time.sleep(60)
jobstring = processCmd('bjobs | grep GSD | wc -l').split('\n')[1]
while jobstring != '0':
    print "GSD jobs still running"
    time.sleep(60)
    jobstring = processCmd('bjobs')

print "about to submit RECO jobs"
print "PDGid = ",PDGid
print "PT = ",PT
os.system('./edSubmitGunImproved.sh RECO '+PDGid+' '+PT)

print "DONE - RECO jobs are submitted"

#time.sleep(60)
#jobstring = processCmd('bjobs | grep RECO | wc -l').split('\n')[1]
#while jobstring != '0':
#    print "RECO jobs still running"
#    time.sleep(60)
#    jobstring = processCmd('bjobs')
#
#print "about to submit NTUP jobs"
#print "PDGid = ",PDGid
#print "PT = ",PT
#os.system('./edSubmitGunImproved.sh NTUP '+PDGid+' '+PT)
#
#print ""
#print "DONE - NTUP jobs are submitted"
