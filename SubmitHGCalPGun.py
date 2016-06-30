###!/usr/bin/python
###-----------------------------------------------
### Latest update: 2016.06.27
###-----------------------------------------------
import sys, os, pwd, commands
import optparse, shlex, re
import time
from time import gmtime, strftime
import math

### function for parsing input options
def parseOptions():

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-t', '--tag',    dest='TAG',    type='string', default='',   help='tag to be appended to the resulting output dir, default is an empty string')
    parser.add_option('-q', '--queue',  dest='QUEUE',  type='string', default='1nh',help='queue to be used with LSF batch, default is 1nh')
    parser.add_option('-n', '--nevts',  dest='NEVTS',  type=int,      default=100,  help='total number of events')
    parser.add_option('-e', '--evtsperjob',dest='EVTSPERJOB', type=int,default=50,   help='number of events per job')
    parser.add_option('-c', '--cfg',    dest='CONFIGFILE', type='string', default='templates/partGun_GSD_template.py', help='CMSSW config template')
    parser.add_option('-p', '--partID', dest='PARTID', type='string', default='22', help='particle PDG ID, empty string to run on all supported: 11,13,22,111,211, default is 22 (photon)')
    parser.add_option(  '', '--pTmin',  dest='pTmin',  type=float, default=1.0,     help='min. pT value')
    parser.add_option(  '', '--pTmax',  dest='pTmax',  type=float, default=35.0,    help='max. pT value')
    parser.add_option(  '', '--local',  action='store_true', dest='LOCAL', default=False, help='Store output dir locally instead of at EOS CMG area, default is False.')
    parser.add_option('-y', '--dry-run', action='store_true', dest='DRYRUN', default=False, help='Perform a dry run (no jobs are lauched).')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

    # list of supported particles, check if requested partID is supported
    global particles
    particles = ['22', '111', '211', '11', '13']
    if not (opt.PARTID in particles or opt.PARTID==''):
        parser.error('Particle with ID ' + opt.PARTID + ' is not supported. Exiting...')
        sys.exit()
    if not (opt.PARTID==''):
        particles = []
        particles.append(opt.PARTID)


### function for processing the external os commands
def processCmd(cmd, quite = 0):
    #    print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

### main function
def submitHGCalParticleGun():

    # parse the arguments and options
    global opt, args, particles
    parseOptions()

    # save working dir
    currentDir = os.getcwd()
    CMSSW_BASE = os.getenv('CMSSW_BASE')
    CMSSW_VERSION = os.getenv('CMSSW_VERSION')
    SCRAM_ARCH = os.getenv('SCRAM_ARCH')

    # prepare tag, prepare/check out dirs
    tag = opt.TAG+'_'+time.strftime("%Y%m%d")
    outDir='partGun_'+tag
    if (not os.path.isdir(outDir)):
        processCmd('mkdir -p '+outDir+'/cfg/')
        processCmd('mkdir -p '+outDir+'/std/')
    else:
        print 'Directory '+outDir+' already exists. Exiting...'
        sys.exit()
    # prepare dir for GSD outputs locally or at EOS
    if (opt.LOCAL):
        processCmd('mkdir -p '+outDir+'/GSD/')
    else:
        processCmd('/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select mkdir -p /eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/'+outDir+'/GSD/');

    # submit all the jobs
    print '[Submitting jobs]'
    njobs = int(math.ceil(float(opt.NEVTS)/float(opt.EVTSPERJOB)))
    jobCount=0
    for particle in particles:
        for job in range(1,int(njobs)+1):
            print 'Submitting job '+str(job)+' out of '+str(njobs)+' for particle ID '+particle
            # prepare the out file and cfg file by replacing DUMMY entries according to input options
            basename = 'partGun_PDGid'+particle+'_x'+str(opt.EVTSPERJOB)+'_Pt'+str(opt.pTmin)+'To'+str(opt.pTmax)+'_GSD_'+str(job)
            cfgfile = basename +'.py'
            outfile = basename +'.root'
            processCmd('cp '+opt.CONFIGFILE+' '+outDir+'/cfg/'+cfgfile)
            processCmd("sed -i 's~DUMMYEVTSPERJOB~"+str(opt.EVTSPERJOB)+"~g' "+outDir+'/cfg/'+cfgfile)
            processCmd("sed -i 's~DUMMYFILENAME~"+outfile+"~g' "+outDir+'/cfg/'+cfgfile)
            processCmd("sed -i 's~DUMMYID~"+particle+"~g' "+outDir+'/cfg/'+cfgfile)
            processCmd("sed -i 's~DUMMYPTMIN~"+str(opt.pTmin)+"~g' "+outDir+'/cfg/'+cfgfile)
            processCmd("sed -i 's~DUMMYPTMAX~"+str(opt.pTmax)+"~g' "+outDir+'/cfg/'+cfgfile)

            #TODO The number of particles could also be a parameter and then the vint32 in the cfg just replaced with

            # submit job
            cmd = 'bsub -o '+outDir+'/std/'+basename +'.out -e '+outDir+'/std/'+basename +'.err -q '+opt.QUEUE+' -J '+cfgfile+' "SubmitFileGSD.sh '+currentDir+' '+outDir+' '+cfgfile+' '+str(opt.LOCAL)+' '+CMSSW_VERSION+' '+CMSSW_BASE+' '+SCRAM_ARCH+'"'

            #TODO This could probably be better handled by a job array
            #Example: bsub -J "foo[1-3]" -oo "foo.%I.out" -eo "foo.%I.err" -q 8nm "sleep 1"
            #This and more at https://www.ibm.com/support/knowledgecenter/SSETD4_9.1.3/lsf_command_ref/bsub.man_top.1.html

            if(opt.DRYRUN):
                print 'Dry-run: ['+cmd+']'
            else:
                output = processCmd(cmd)
    #            while ('error' in output):
    #                time.sleep(1.0);
    #                output = processCmd(cmd)
    #                if ('error' not in output):
    #                    print 'Submitted after retry - job '+str(jobCount+1)


            jobCount += 1

    print '[Submitted '+str(jobCount)+' jobs]'

### run the submitAnalyzer() as main function
if __name__ == "__main__":
    submitHGCalParticleGun()
