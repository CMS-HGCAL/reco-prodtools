#! /usr/bin/env python
import os
import commands
import time

def processCmd(cmd, quite = 0):
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output


PDGid='22'
PT='35'


print "about to submit GSD jobs"
os.system('./edSubmitGunImproved.sh GSD '+PDGid+' '+PT)

time.sleep(10)
jobstring = processCmd('bjobs')
while jobstring != 'No unfinished job found':
    print "GSD jobs still running"
    time.sleep(10)
    jobstring = processCmd('bjobs')

print "about to submit RECO jobs"
os.system('./edSubmitGunImproved.sh RECO '+PDGid+' '+PT)

time.sleep(60)
jobstring = processCmd('bjobs')
while jobstring != 'No unfinished job found':
    print "RECO jobs still running"
    time.sleep(60)
    jobstring = processCmd('bjobs')

print "about to submit NTUP jobs"
os.system('./edSubmitGunImproved.sh NTUP '+PDGid+' '+PT)

print ""
print "DONE - NTUP jobs are submitted"
