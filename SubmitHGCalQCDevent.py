###!/usr/bin/python
import sys
import os
import commands
import optparse
import fnmatch
import time
import math
import re

eosExec = 'eos'

### parsing input options
def parseOptions():

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-t', '--tag',    dest='TAG',    type='string',  default='', help='tag to be appended to the resulting output dir, default is an empty string')
    parser.add_option('-q', '--queue',  dest='QUEUE',  type='string',  default='tomorrow', help='queue to be used with HTCondor, default is tomorrow')
    parser.add_option('-n', '--nevts',  dest='NEVTS',  type=int,       default=100,  help='total number of events, applicable to runs with GEN stage, default is 100')
    parser.add_option('-e', '--evtsperjob', dest='EVTSPERJOB', type=int, default=-1,   help='number of events per job, if set to -1 it will set to a recommended value (GSD: 4events/1nh, RECO:8events/1nh), default is -1')
    parser.add_option('-c', '--cfg',    dest='CONFIGFILE', type='string', default='',help='CMSSW config template name, if empty string the deafult one will be used')
    parser.add_option('-p', '--partID', dest='PARTID', type='string',     default='', help='string of particle PDG IDs separated by comma, if empty string - run on all supported (11,12,13,14,15,16,22,111,211,130) and corresponding negative values, default is empty string (all)')
    parser.add_option('', '--thresholdMin',  dest='thresholdMin',  type=float, default=1.0,     help='min. threshold value')
    parser.add_option('', '--thresholdMax',  dest='thresholdMax',  type=float, default=35.0,    help='max. threshold value')
    parser.add_option('', '--etaMin',  dest='etaMin',  type=float, default=1.479,  help='min. eta value')
    parser.add_option('', '--etaMax',  dest='etaMax',  type=float, default=3.0,    help='max. eta value')

    parser.add_option('-l', '--local',  action='store_true', dest='LOCAL',  default=False, help='store output dir locally instead of at EOS CMG area, default is False.')
    parser.add_option('-y', '--dry-run', action='store_true', dest='DRYRUN', default=False, help='perform a dry run (no jobs are lauched).')
    parser.add_option('', '--eosArea', dest='eosArea', type='string', default='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production', help='path to the eos area where the output jobs will be staged out')
    parser.add_option('-d', '--datTier', dest='DTIER',  type='string', default='GSD', help='data tier to run: "GSD" (GEN-SIM-DIGI) or "RECO", default is "GSD"')
    parser.add_option('-i', '--inDir',  dest='inDir',  type='string', default='',   help='name of the previous stage dir (relative to the local submission or "eosArea"), to be used as the input for next stage, not applicable for GEN stage')
    parser.add_option('-r', '--RelVal',  dest='RELVAL',  type='string', default='',   help='name of relval reco dataset to be ntuplized (currently implemented only for NTUP data Tier')
    parser.add_option('', '--noReClust',  action='store_false', dest='RECLUST',  default=True, help='do not re-run RECO-level clustering at NTUP step, default is True (do re-run the clustering).')
    parser.add_option('', '--addGenOrigin',    action='store_true', dest='ADDGENORIG',  default=False, help='add coordinates of the origin vertex for gen particles as well as the mother particle index')
    parser.add_option('', '--addGenExtrapol',  action='store_true', dest='ADDGENEXTR',  default=False, help='add coordinates for the position of each gen particle extrapolated to the first HGCal layer (takes into account magnetic field)')
    parser.add_option('', '--storePFCandidates',  action='store_true', dest='storePFCandidates',  default=False, help='store PFCandidates collection')
    parser.add_option('', '--multiClusterTag',  action='store', dest='MULTICLUSTAG', default="hgcalMultiClusters", help='name of HGCalMultiCluster InputTag - use hgcalLayerClusters before CMSSW_10_3_X')
    parser.add_option('', '--keepDQMfile',  action='store_true', dest='DQM',  default=False, help='store the DQM file in relevant folder locally or in EOS, default is False.')


    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

    # sanity check for data tiers
    dataTiers = ['GSD', 'RECO', 'NTUP']
    if opt.DTIER not in dataTiers:
        parser.error('Data tier ' + opt.DTIER + ' is not supported. Exiting...')
        sys.exit()

    # make sure CMSSW is set up
    if 'CMSSW_BASE' not in os.environ:
        print 'ERROR: CMSSW does not seem to be set up. Exiting...'
        sys.exit()

    # set the default config, if not specified in options
    if (opt.CONFIGFILE == ''):
        if(opt.DTIER == 'GSD'):
            opt.CONFIGFILE = 'templates/eventQCD_'+opt.DTIER+'_template.py'
        else:
            opt.CONFIGFILE = 'templates/partGun_'+opt.DTIER+'_template.py'
  

    # supported queues with the recommended number of events per hour (e.g. ~4events/1nh for GSD, ~8events/1nh for RECO) + sanity check
    eventsPerHour = {'GSD':4, 'RECO':8, 'NTUP':100}
    queues_evtsperjob = {'nextweek':(7*24*eventsPerHour[opt.DTIER]), 'testmatch':(2*24*eventsPerHour[opt.DTIER]), 'tomorrow':(1*24*eventsPerHour[opt.DTIER]), 'workday':(8*eventsPerHour[opt.DTIER]), 'longlunch':(1*eventsPerHour[opt.DTIER]), 'microcentury':(1*eventsPerHour[opt.DTIER]), 'espresso':(1)}
    if opt.QUEUE not in queues_evtsperjob.keys():
        parser.error('Queue ' + opt.QUEUE + ' is not supported. Exiting...')
        sys.exit()
    else:
        if opt.EVTSPERJOB==-1:
            opt.EVTSPERJOB = queues_evtsperjob[opt.QUEUE] # set the recommnded number of events per job, if requested

### processing the external os commands
def processCmd(cmd, quite = 0):
    #print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

### print the setup
def printSetup(CMSSW_BASE, CMSSW_VERSION, SCRAM_ARCH, currentDir, outDir):
    global opt
    print '--------------------'
    print '[Run parameters]'
    print '--------------------'
    print 'DATA TIER:  ', [opt.DTIER, 'GEN-SIM-DIGI'][int(opt.DTIER=='GSD')]
    print 'CMSSW BASE: ', CMSSW_BASE
    print 'CMSSW VER:  ', CMSSW_VERSION,'[', SCRAM_ARCH, ']'
    print 'CONFIGFILE: ', opt.CONFIGFILE
    # relval takes precedence...
    if (opt.RELVAL == ''):
        curr_input= opt.inDir
    else:
        curr_input= opt.RELVAL
    print 'INPUTS:     ', [curr_input, ' times per event, ' + ' threshold in ['+str(opt.thresholdMin)+','+str(opt.thresholdMax)+'], eta threshold in ['+str(opt.etaMin)+','+str(opt.etaMax)+']',opt.RELVAL][int(opt.DTIER=='GSD')]
    print 'STORE AREA: ', [opt.eosArea, currentDir][int(opt.LOCAL)]
    print 'OUTPUT DIR: ', outDir
    print 'QUEUE:      ', opt.QUEUE
    print ['NUM. EVTS:   '+str(opt.NEVTS), ''][int(opt.DTIER!='GSD')]
    print '--------------------'

### prepare the list of input GSD files for RECO stage
def getInputFileList(DASquery,inPath, inSubDir, local, pattern):
    inputList = []
    if not DASquery:
        if (local):
            inputList = [f for f in os.listdir(inPath+'/'+inSubDir) if (os.path.isfile(os.path.join(inPath+'/'+inSubDir, f)) and (fnmatch.fnmatch(f, pattern)))]
        else:
            # this is a work-around, need to find a proper way to do it for EOS
            inputList = [f for f in processCmd(eosExec + ' ls ' + inPath+'/'+inSubDir+'/').split('\n') if ( (processCmd(eosExec + ' fileinfo ' + inPath+'/'+inSubDir+'/' + f).split(':')[0].lstrip() == 'File') and (fnmatch.fnmatch(f, pattern)))]
    else:
        # DASquery will be made based on inPath (i.e. opt.RELVAL)

        relvalname=inPath.split('/')[1]
        cmd='dasgoclient -limit 10000 -query="file dataset='+inPath+'" | grep '+relvalname
        status, thisoutput = commands.getstatusoutput(cmd)
        if status !=0:
            print "Error in processing command: "+cmd
            print "Did you forget running voms-proxy-init?"
            sys.exit(1)
        inputList=thisoutput.split()

    return inputList

### submission of GSD/RECO production
def submitHGCalProduction():

    # parse the arguments and options
    global opt, args
    parseOptions()

    # save working dir
    currentDir = os.getcwd()
    CMSSW_BASE = os.getenv('CMSSW_BASE')
    CMSSW_VERSION = os.getenv('CMSSW_VERSION')
    SCRAM_ARCH = os.getenv('SCRAM_ARCH')
    commonFileNamePrefix = 'eventQCD'

    # RELVAL
    DASquery=False
    if opt.RELVAL != '':
        DASquery=True

    # previous data tier
    previousDataTier = ''
    if (opt.DTIER == 'RECO'):
        previousDataTier = 'GSD'
    elif (opt.DTIER == 'NTUP'):
        previousDataTier = 'RECO'

    # prepare tag, prepare/check out dirs
    tag = "_".join([opt.TAG, time.strftime("%Y%m%d")])
    if (opt.DTIER == 'GSD'):
        outDir = "_".join([commonFileNamePrefix, tag])
        if (not os.path.isdir(outDir)):
            processCmd('mkdir -p '+outDir+'/cfg/')
            processCmd('mkdir -p '+outDir+'/std/')
            processCmd('mkdir -p '+outDir+'/jobs/')
        else:
            print 'Directory '+outDir+' already exists. Exiting...'
            sys.exit()
    elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        if not DASquery:
            outDir = opt.inDir
        else:
            # create an ouput directory based on relval name
            outDir=opt.RELVAL.replace('/','_')
        processCmd('mkdir -p '+outDir+'/cfg/')
        processCmd('mkdir -p '+outDir+'/std/')
        processCmd('mkdir -p '+outDir+'/jobs/')


  # prepare dir for GSD outputs locally or at EOS
    if (opt.LOCAL):
        processCmd('mkdir -p '+outDir+'/'+opt.DTIER+'/')
        recoInputPrefix = 'file:'+currentDir+'/'+outDir+'/'+previousDataTier+'/'
        if (opt.DQM): processCmd('mkdir -p '+outDir+'/DQM/')
    else:
        processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/'+opt.DTIER+'/');
        recoInputPrefix = 'root://eoscms.cern.ch/'+opt.eosArea+'/'+outDir+'/'+previousDataTier+'/'
        if (opt.DQM): processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/DQM/'); 
    # in case of relval always take reconInput from /store...
    if DASquery: recoInputPrefix=''

    # determine number of jobs for GSD, in case of 'RECO'/'NTUP' only get the input GSD/RECO path

    if (opt.DTIER == 'GSD'):
        njobs = int(math.ceil(float(opt.NEVTS)/float(opt.EVTSPERJOB)))
    elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        inPath = [opt.eosArea+'/'+opt.inDir, currentDir+'/'+opt.inDir][opt.LOCAL]
        if DASquery: inPath=opt.RELVAL

    # print out some info
    printSetup(CMSSW_BASE, CMSSW_VERSION, SCRAM_ARCH, currentDir, outDir)

    # submit all the jobs
    print '[Submitting jobs]'
    jobCount=0

    # read the template file in a single string
    f_template= open(opt.CONFIGFILE, 'r')
    template= f_template.read()
    f_template.close()

    nFilesPerJob = 0
    eventsPerPrevJob = 0
    # in case of 'RECO' or 'NTUP', get the input file list for given particle, determine number of jobs, get also basic GSD/RECO info
    if (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        inputFilesList = getInputFileList(DASquery,inPath, previousDataTier, opt.LOCAL, commonFileNamePrefix+'_*.root')
        
        # build regular expression for splitting (NOTE: none of this is used for relval!)
        if not DASquery:
            regex = re.compile(ur"eventQCD_x([0-9]*)_([0-9]*[.]?[0-9]*)To([0-9]*[.]?[0-9]*)_.*\.root")
            matches = regex.match(inputFilesList[0])
            eventsPerPrevJob = int(matches.group(1))
            opt.thresholdMin = float(matches.group(2))
            opt.thresholdMax = float(matches.group(3))
            nFilesPerJob = max(int(math.floor(float(min(opt.EVTSPERJOB, len(inputFilesList)*eventsPerPrevJob))/float(eventsPerPrevJob))),1)
            njobs = int(math.ceil(float(len(inputFilesList))/float(nFilesPerJob)))
        else:
            njobs=len(inputFilesList)
            nFilesPerJob = 1

    for job in range(1,int(njobs)+1):
        submittxt=' for QCD event'
        if DASquery : submittxt=' for RelVal:'+opt.RELVAL
        print 'Submitting job '+str(job)+' out of '+str(njobs)+submittxt

        # prepare the out file and cfg file by replacing DUMMY entries according to input options
        if DASquery:
            basename=outDir+'_'+opt.DTIER+'_'+str(job)
        else:
            basename = commonFileNamePrefix + '_x'+str([nFilesPerJob * eventsPerPrevJob, opt.EVTSPERJOB][opt.DTIER=='GSD'])+'_' +str(opt.thresholdMin)+'To'+str(opt.thresholdMax)+'_'+opt.DTIER+'_'+str(job)

        cfgfile = basename +'.py'
        outfile = basename +'.root'
        outdqmfile = basename.replace(opt.DTIER, 'DQM') +'.root'
        jobfile = basename +'.sub'

        s_template=template

        s_template=s_template.replace('DUMMYFILENAME',outfile)
        s_template=s_template.replace('DUMMYDQMFILENAME',outdqmfile)
        s_template=s_template.replace('DUMMYSEED',str(job))

        if (opt.DTIER == 'GSD'):
            # prepare GEN-SIM-DIGI inputs
            s_template=s_template.replace('DUMMYEVTSPERJOB',str(opt.EVTSPERJOB))
            s_template=s_template.replace('DUMMYTHRESHMIN',str(opt.thresholdMin))
            s_template=s_template.replace('DUMMYTHRESHMAX',str(opt.thresholdMax))
            s_template=s_template.replace('DUMMYETAMIN',str(opt.etaMin))
            s_template=s_template.replace('DUMMYETAMAX',str(opt.etaMax))
            s_template=s_template.replace('MAXTHRESHSTRING',"Max")
            s_template=s_template.replace('MINTHRESHSTRING',"Min")

        elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
            # prepare RECO inputs
            inputFilesListPerJob = inputFilesList[(job-1)*nFilesPerJob:(job)*nFilesPerJob]
            if len(inputFilesListPerJob)==0: continue
            inputFiles = '"' + '", "'.join([recoInputPrefix+str(f) for f in inputFilesListPerJob]) + '"'
            s_template=s_template.replace('DUMMYINPUTFILELIST',inputFiles)
            s_template=s_template.replace('DUMMYEVTSPERJOB',str(-1))



        if (opt.DTIER == 'NTUP'):
            s_template=s_template.replace('DUMMYRECLUST',str(opt.RECLUST))
            s_template=s_template.replace('DUMMYSGO',str(opt.ADDGENORIG))
            s_template=s_template.replace('DUMMYSGE',str(opt.ADDGENEXTR))
            s_template=s_template.replace('DUMMYSPFC',str(opt.storePFCandidates))
            s_template=s_template.replace('DUMMYMULCLUSTAG', str(opt.MULTICLUSTAG))

        # submit job
        # now write the file from the s_template

        write_template= open(outDir+'/cfg/'+cfgfile, 'w')
        write_template.write(s_template)
        write_template.close()

        write_condorjob= open(outDir+'/jobs/'+jobfile, 'w')
        write_condorjob.write('+JobFlavour = "'+opt.QUEUE+'" \n\n')
        write_condorjob.write('executable  = '+currentDir+'/SubmitFileGSD.sh \n')
        write_condorjob.write('arguments   = $(ClusterID) $(ProcId) '+currentDir+' '+outDir+' '+cfgfile+' '+str(opt.LOCAL)+' '+CMSSW_VERSION+' '+CMSSW_BASE+' '+SCRAM_ARCH+' '+opt.eosArea+' '+opt.DTIER+' '+str(opt.DQM)+'\n')
        write_condorjob.write('output      = '+outDir+'/std/'+basename+'.out \n')
        write_condorjob.write('error       = '+outDir+'/std/'+basename+'.err \n')
        write_condorjob.write('log         = '+outDir+'/std/'+basename+'_htc.log \n\n')
        write_condorjob.write('max_retries = 1\n')
        write_condorjob.write('queue \n')
        write_condorjob.close()

        cmd = 'condor_submit ' + currentDir+'/'+outDir+'/jobs/'+jobfile

        #TODO This could probably be better handled by a job array
        #Example: bsub -J "foo[1-3]" -oo "foo.%I.out" -eo "foo.%I.err" -q 8nm "sleep 1"
        #This and more at https://www.ibm.com/support/knowledgecenter/SSETD4_9.1.3/lsf_command_ref/bsub.man_top.1.html

        if(opt.DRYRUN):
            print 'Dry-run: ['+cmd+']'
        else:
            output = processCmd(cmd)
            while ('error' in output):
                time.sleep(1.0);
                output = processCmd(cmd)
                if ('error' not in output):
                    print 'Submitted after retry - job '+str(jobCount+1)


        jobCount += 1

    print '[Submitted '+str(jobCount)+' jobs]'

### run the submitHGCalProduction() as main
if __name__ == "__main__":
    submitHGCalProduction()
