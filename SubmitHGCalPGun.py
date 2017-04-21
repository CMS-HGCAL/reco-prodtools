###!/usr/bin/python
import sys
import os
import commands
import optparse
import fnmatch
import time
import math
import re

eosExec = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'


### parsing input options
def parseOptions():

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-t', '--tag',    dest='TAG',    type='string',  default='', help='tag to be appended to the resulting output dir, default is an empty string')
    parser.add_option('-q', '--queue',  dest='QUEUE',  type='string',  default='1nd', help='queue to be used with LSF batch, default is 1nd')
    parser.add_option('-n', '--nevts',  dest='NEVTS',  type=int,       default=100,  help='total number of events, applicable to runs with GEN stage, default is 100')
    parser.add_option('-e', '--evtsperjob', dest='EVTSPERJOB', type=int, default=-1,   help='number of events per job, if set to -1 it will set to a recommended value (GSD: 4events/1nh, RECO:8events/1nh), default is -1')
    parser.add_option('-c', '--cfg',    dest='CONFIGFILE', type='string', default='',help='CMSSW config template name, if empty string the deafult one will be used')
    parser.add_option('-p', '--partID', dest='PARTID', type='string',     default='', help='particle PDG ID, if empty string - run on all supported (11,12,13,14,15,16,22,111,211), default is empty string (all)')
    parser.add_option('', '--nPart',  dest='NPART',  type=int,   default=10,      help='number of particles of type PARTID to be generated per event, default is 10')
    parser.add_option('', '--thresholdMin',  dest='thresholdMin',  type=float, default=1.0,     help='min. threshold value')
    parser.add_option('', '--thresholdMax',  dest='thresholdMax',  type=float, default=35.0,    help='max. threshold value')
    parser.add_option('', '--gunType',   dest='gunType',   type='string', default='Pt',    help='Pt or E gun')
    parser.add_option('', '--PU',   dest='PU',   type='string', default='0',    help='PU value (0 is the default)')
    parser.add_option('', '--PUDS',   dest='PUDS',   type='string', default='',    help='PU dataset')
    parser.add_option('', '--InConeID', dest='InConeID',   type='string',     default='', help='PDG ID for particle to be generated in the cone (supported as PARTID), default is empty string (none)')
    parser.add_option('', '--MinDeltaR',  dest='MinDeltaR',  type=float, default=0.3, help='min. DR value')
    parser.add_option('', '--MaxDeltaR',  dest='MaxDeltaR',  type=float, default=0.4, help='max. DR value')
    parser.add_option('', '--MinMomRatio',  dest='MinMomRatio',  type=float, default=0.5, help='min. momentum ratio for particle inside of the cone and particle that defines the cone')
    parser.add_option('', '--MaxMomRatio',  dest='MaxMomRatio',  type=float, default=2.0, help='max. momentum ratio for particle inside of the cone and particle that defines the cone')
    parser.add_option('-l', '--local',  action='store_true', dest='LOCAL',  default=False, help='store output dir locally instead of at EOS CMG area, default is False.')
    parser.add_option('-y', '--dry-run', action='store_true', dest='DRYRUN', default=False, help='perform a dry run (no jobs are lauched).')
    parser.add_option('', '--eosArea', dest='eosArea', type='string', default='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production', help='path to the eos area where the output jobs will be staged out')
    parser.add_option('-d', '--datTier', dest='DTIER',  type='string', default='GSD', help='data tier to run: "GSD" (GEN-SIM-DIGI) or "RECO", default is "GSD"')
    parser.add_option('-i', '--inDir',  dest='inDir',  type='string', default='',   help='name of the previous stage dir (relative to the local submission or "eosArea"), to be used as the input for next stage, not applicable for GEN stage')
    parser.add_option('-r', '--RelVal',  dest='RELVAL',  type='string', default='',   help='name of relval reco dataset to be ntuplized (currently implemented only for NTUP data Tier')

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

    partGunTypes = ['Pt', 'E']
    if opt.gunType not in partGunTypes:
        parser.error('Particle gun type ' + opt.gunType + ' is not supported. Exiting...')
        sys.exit()

    # set the default config, if not specified in options
    if (opt.CONFIGFILE == ''):
        opt.CONFIGFILE = 'templates/partGun_'+opt.DTIER+'_template.py'

    # supported queues with the recommended number of events per hour (e.g. ~4events/1nh for GSD, ~8events/1nh for RECO) + sanity check
    eventsPerHour = {'GSD':4, 'RECO':8, 'NTUP':100}
    queues_evtsperjob = {'1nw':(7*24*eventsPerHour[opt.DTIER]), '2nd':(2*24*eventsPerHour[opt.DTIER]), '1nd':(1*24*eventsPerHour[opt.DTIER]), '8nh':(8*eventsPerHour[opt.DTIER]), '1nh':(1*eventsPerHour[opt.DTIER]), '8nm':(1)}
    if opt.QUEUE not in queues_evtsperjob.keys():
        parser.error('Queue ' + opt.QUEUE + ' is not supported. Exiting...')
        sys.exit()
    else:
        if opt.EVTSPERJOB==-1:
            opt.EVTSPERJOB = queues_evtsperjob[opt.QUEUE] # set the recommnded number of events per job, if requested

    # list of supported particles, check if requested partID is supported
    global particles
    particles = ['22', '111', '211', '11', '13', '15', '12', '14', '16']
    if not (opt.PARTID in particles or opt.PARTID == ''):
        parser.error('Particle with ID ' + opt.PARTID + ' is not supported. Exiting...')
        sys.exit()

    # sanity check for generation of particle within the cone (require to be compatibe with NPART==1 and supported particles)
    if (opt.InConeID != '') and (opt.InConeID not in particles or opt.NPART != 1):
        print opt.InConeID in particles
        parser.error('InCone particle with ID {} is not supported, or incompatible with NPART {}. Exiting...'.format(opt.InConeID, opt.NPART))
        sys.exit()

    if not (opt.PARTID == ''):
        particles = []
        particles.append(opt.PARTID)

    # overwrite for RelVal
    if opt.RELVAL != '':
        particles = ['dummy']

    # sanity check on PU
    if int(opt.PU) !=0:
        if opt.DTIER != 'GSD':
            parser.error('PU simulation not supported for ' + opt.DTIER + '. Exiting...')
            sys.exit(1)
        if opt.PUDS == '':
            parser.error('PU simulation requested you need to specify a dataset (--PUDS). Exiting...')
            sys.exit(1)

### processing the external os commands
def processCmd(cmd, quite = 0):
    #    print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

### print the setup
def printSetup(CMSSW_BASE, CMSSW_VERSION, SCRAM_ARCH, currentDir, outDir):
    global opt, particles
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
    print 'PU:         ',opt.PU
    print 'PU dataset: ',opt.PUDS
    print 'INPUTS:     ', [curr_input, 'Particle gun type: ' + opt.gunType + ', PDG ID '+str(opt.PARTID)+', '+str(opt.NPART)+' per event, ' + opt.gunType + ' threshold in ['+str(opt.thresholdMin)+','+str(opt.thresholdMax)+']',opt.RELVAL][int(opt.DTIER=='GSD')]

    print 'INPUTS:     ', [curr_input, 'Particle gun type: ' + opt.gunType + ', PDG ID '+str(opt.PARTID)+', '+str(opt.NPART)+' per event, ' + opt.gunType + ' threshold in ['+str(opt.thresholdMin)+','+str(opt.thresholdMax)+']',opt.RELVAL][int(opt.DTIER=='GSD')]
    if (opt.InConeID!='' and opt.DTIER=='GSD'):
        print '    IN-CONE: PDG ID '+str(opt.InConeID)+', deltaR in ['+str(opt.MinDeltaR)+ ','+str(opt.MaxDeltaR)+']'+', momentum ratio in ['+str(opt.MinMomRatio)+ ','+str(opt.MaxMomRatio)+']'

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
        cmd='das_client --limit 10000 --query="file dataset='+inPath+'" | grep '+relvalname
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
    global opt, args, particles
    parseOptions()

    # save working dir
    currentDir = os.getcwd()
    CMSSW_BASE = os.getenv('CMSSW_BASE')
    CMSSW_VERSION = os.getenv('CMSSW_VERSION')
    SCRAM_ARCH = os.getenv('SCRAM_ARCH')
    commonFileNamePrefix = 'partGun'
    partGunType = 'FlatRandom%sGunProducer' % opt.gunType
    if opt.InConeID != '':
        partGunType = 'MultiParticleInConeGunProducer'  # change part gun type if needed, keep opt.gunType unchanged (E or Pt) for the "primary particle"

    # RELVAL
    DASquery=False
    if opt.RELVAL != '':
        DASquery=True

    # in case of PU, GSD needs the MinBias
    if int(opt.PU) != 0:
        # we need to get the PU dataset
        puname=str(opt.PUDS).split('/')[1]
        # PLEASE NOTE --> using only 20 MinBias files here!! change to to 10000 if you want them all
        cmd='das_client --limit 20 --query="file dataset='+str(opt.PUDS)+'" | grep '+puname
        status, thisoutput = commands.getstatusoutput(cmd)
        if status !=0:
            print "Error in processing command: "+cmd
            print "Did you forget running voms-proxy-init?"
            sys.exit(1)
        PUList=thisoutput.split()
        # define as well the template to be added
        PUSECTION="""
process.RandomNumberGeneratorService.mix.initialSeed = cms.untracked.uint32(PUSEED)
process.mix.input.nbPileupEvents.averageNumber = cms.double(PUVALUE)
process.mix.input.fileNames = cms.untracked.vstring(PUFILES)
process.mix.bunchspace = cms.int32(25)
process.mix.minBunch = cms.int32(-12)
process.mix.maxBunch = cms.int32(3)
        """
        PUSECTION=PUSECTION.replace('PUVALUE',opt.PU)
        PUSECTION=PUSECTION.replace('PUFILES',str(PUList))
        # print PUSECTION

    # in case of InCone generation of particles
    if opt.InConeID != '':
        InConeSECTION="""
        InConeID = cms.vint32(DUMMYInConeID),
        MinDeltaR = cms.double(DUMMYMinDeltaR),
        MaxDeltaR = cms.double(DUMMYMaxDeltaR),
        MinMomRatio = cms.double(DUMMYMinMomRatio),
        MaxMomRatio = cms.double(DUMMYMaxMomRatio),
        InConeMinEta = cms.double(1.479),
        InConeMaxEta = cms.double(3.0),
        InConeMinPhi = cms.double(-3.14159265359),
        InConeMaxPhi = cms.double(3.14159265359),
        InConeMaxTry = cms.uint32(10),
        """
        InConeSECTION=InConeSECTION.replace('DUMMYInConeID', opt.InConeID)
        InConeSECTION=InConeSECTION.replace('DUMMYMinDeltaR', str(opt.MinDeltaR))
        InConeSECTION=InConeSECTION.replace('DUMMYMaxDeltaR', str(opt.MaxDeltaR))
        InConeSECTION=InConeSECTION.replace('DUMMYMinMomRatio', str(opt.MinMomRatio))
        InConeSECTION=InConeSECTION.replace('DUMMYMaxMomRatio', str(opt.MaxMomRatio))


    # previous data tier
    previousDataTier = ''
    if (opt.DTIER == 'RECO'):
        previousDataTier = 'GSD'
    elif (opt.DTIER == 'NTUP'):
        previousDataTier = 'RECO'

    # prepare tag, prepare/check out dirs
    tag = "_".join([opt.TAG, time.strftime("%Y%m%d")])
    if (opt.DTIER == 'GSD'):
        outDir = "_".join([partGunType, tag])
        if (not os.path.isdir(outDir)):
            processCmd('mkdir -p '+outDir+'/cfg/')
            processCmd('mkdir -p '+outDir+'/std/')
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


  # prepare dir for GSD outputs locally or at EOS
    if (opt.LOCAL):
        processCmd('mkdir -p '+outDir+'/'+opt.DTIER+'/')
        recoInputPrefix = 'file:'+currentDir+'/'+outDir+'/'+previousDataTier+'/'
    else:
        processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/'+opt.DTIER+'/');
        recoInputPrefix = 'root://eoscms.cern.ch/'+opt.eosArea+'/'+outDir+'/'+previousDataTier+'/'
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

    for particle in particles:
        nFilesPerJob = 0
        eventsPerPrevJob = 0
        # in case of 'RECO' or 'NTUP', get the input file list for given particle, determine number of jobs, get also basic GSD/RECO info
        if (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
            inputFilesList = getInputFileList(DASquery,inPath, previousDataTier, opt.LOCAL, commonFileNamePrefix+'*_PDGid'+particle+'_*.root')
            if len(inputFilesList) == 0:
                continue
            # build regular expression for splitting (NOTE: none of this is used for relval!)
            if not DASquery:
                regex = re.compile(ur"partGun_PDGid[0-9]*_x([0-9]*)_(E|Pt)([0-9]*[.]?[0-9]*)To([0-9]*[.]?[0-9]*)_.*\.root")
                matches = regex.match(inputFilesList[0])
                eventsPerPrevJob = int(matches.group(1))
                opt.gunType = matches.group(2)
                opt.thresholdMin = float(matches.group(3))
                opt.thresholdMax = float(matches.group(4))
                nFilesPerJob = max(int(math.floor(float(min(opt.EVTSPERJOB, len(inputFilesList)*eventsPerPrevJob))/float(eventsPerPrevJob))),1)
                njobs = int(math.ceil(float(len(inputFilesList))/float(nFilesPerJob)))
            else:
                njobs=len(inputFilesList)
                nFilesPerJob = 1

        for job in range(1,int(njobs)+1):
            submittxt=' for particle ID '+particle
            if DASquery : submittxt=' for RelVal:'+opt.RELVAL
            print 'Submitting job '+str(job)+' out of '+str(njobs)+submittxt

            # prepare the out file and cfg file by replacing DUMMY entries according to input options
            if DASquery:
                basename=outDir+'_'+opt.DTIER+'_'+str(job)
            else:
                basename = commonFileNamePrefix + '_PDGid'+particle+'_x'+str([nFilesPerJob * eventsPerPrevJob, opt.EVTSPERJOB][opt.DTIER=='GSD'])+'_' + opt.gunType+str(opt.thresholdMin)+'To'+str(opt.thresholdMax)+'_'+opt.DTIER+'_'+str(job)

            cfgfile = basename +'.py'
            outfile = basename +'.root'

            s_template=template

            s_template=s_template.replace('DUMMYFILENAME',outfile)
            s_template=s_template.replace('DUMMYSEED',str(job))

            if (opt.DTIER == 'GSD'):
                # first prepare replaces for PU
                if int(opt.PU) == 0:
                    # no PU
                    mixing='mixNoPU_cfi'
                else:
                    mixing='mix_POISSON_average_cfi'
                    s_template=s_template.replace('#DUMMYPUSECTION',PUSECTION)
                    s_template=s_template.replace('PUSEED',str(job))

                # in case of InCone generation of particles
                if opt.InConeID != '':
                    s_template=s_template.replace('#DUMMYINCONESECTION',InConeSECTION)

                # prepare GEN-SIM-DIGI inputs
                nParticles = ','.join([particle for i in range(0,opt.NPART)])
                s_template=s_template.replace('DUMMYEVTSPERJOB',str(opt.EVTSPERJOB))

                s_template=s_template.replace('DUMMYIDs',nParticles)
                s_template=s_template.replace('DUMMYTHRESHMIN',str(opt.thresholdMin))
                s_template=s_template.replace('DUMMYTHRESHMAX',str(opt.thresholdMax))
                s_template=s_template.replace('GUNPRODUCERTYPE',str(partGunType))
                s_template=s_template.replace('MAXTHRESHSTRING',"Max"+str(opt.gunType))
                s_template=s_template.replace('MINTHRESHSTRING',"Min"+str(opt.gunType))
                s_template=s_template.replace('DUMMYPU',str(mixing))


            elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
                # prepare RECO inputs
                inputFilesListPerJob = inputFilesList[(job-1)*nFilesPerJob:(job)*nFilesPerJob]
                if len(inputFilesListPerJob)==0: continue
                inputFiles = '"' + '", "'.join([recoInputPrefix+str(f) for f in inputFilesListPerJob]) + '"'
                s_template=s_template.replace('DUMMYINPUTFILELIST',inputFiles)
                s_template=s_template.replace('DUMMYEVTSPERJOB',str(-1))

                if DASquery:
                    # in case of relval centrally produced use readOfficialReco flag
                    s_template=s_template.replace('DUMMYROR','True')
                else:
                    # otherwise put False
                    s_template=s_template.replace('DUMMYROR','False')

            # submit job
            # now write the file from the s_template

            write_template= open(outDir+'/cfg/'+cfgfile, 'w')
            write_template.write(s_template)
            write_template.close()


            cmd = 'bsub -o '+outDir+'/std/'+basename +'.out -e '+outDir+'/std/'+basename +'.err -q '+opt.QUEUE+' -J '+basename+' "SubmitFileGSD.sh '+currentDir+' '+outDir+' '+cfgfile+' '+str(opt.LOCAL)+' '+CMSSW_VERSION+' '+CMSSW_BASE+' '+SCRAM_ARCH+' '+opt.eosArea+' '+opt.DTIER+'"'

            #TODO This could probably be better handled by a job array
            #Example: bsub -J "foo[1-3]" -oo "foo.%I.out" -eo "foo.%I.err" -q 8nm "sleep 1"
            #This and more at https://www.ibm.com/support/knowledgecenter/SSETD4_9.1.3/lsf_command_ref/bsub.man_top.1.html

            if(opt.DRYRUN):
                print 'Dry-run: ['+cmd+']'
            # else:
            #     output = processCmd(cmd)
            #     while ('error' in output):
            #         time.sleep(1.0);
            #         output = processCmd(cmd)
            #         if ('error' not in output):
            #             print 'Submitted after retry - job '+str(jobCount+1)


            jobCount += 1

    print '[Submitted '+str(jobCount)+' jobs]'

### run the submitHGCalProduction() as main
if __name__ == "__main__":
    submitHGCalProduction()
