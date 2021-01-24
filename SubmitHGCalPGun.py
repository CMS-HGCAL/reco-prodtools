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

def createParser():
    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-t', '--tag',    dest='TAG',    type='string',  default='', help='tag to be appended to the resulting output dir, default is an empty string')
    parser.add_option('-q', '--queue',  dest='QUEUE',  type='string',  default='tomorrow', help='queue to be used with HTCondor, default is tomorrow')
    parser.add_option('-n', '--nevts',  dest='NEVTS',  type=int,       default=100,  help='total number of events, applicable to runs with GEN stage, default is 100')
    parser.add_option('-e', '--evtsperjob', dest='EVTSPERJOB', type=int, default=-1,   help='number of events per job, if set to -1 it will set to a recommended value (GSD: 4events/1nh, RECO:8events/1nh), default is -1')
    parser.add_option('-c', '--cfg',    dest='CONFIGFILE', type='string', default='',help='CMSSW config template name, if empty string the deafult one will be used')
    parser.add_option('-p', '--partID', dest='PARTID', type='string',     default='', help='string of particles\' PDG IDs to shoot, separated by comma')
    parser.add_option('', '--nPart',  dest='NPART',  type=int,   default=1,      help='number of times particles of type(s) PARTID will be generated per event, default is 1')
    parser.add_option('', '--thresholdMin',  dest='thresholdMin',  type=float, default=-1.0, help='min. threshold value, used as min. pt phase space cut for physproc gunmode when >= 0')
    parser.add_option('', '--thresholdMax',  dest='thresholdMax',  type=float, default=-1.0, help='max. threshold value, used as max. pt phase space cut for physproc gunmode when >= 0')
    parser.add_option('', '--etaMin',  dest='etaMin',  type=float, default=1.479,  help='min. eta value')
    parser.add_option('', '--etaMax',  dest='etaMax',  type=float, default=3.0,    help='max. eta value')
    parser.add_option('', '--zMin',  dest='zMin',  type=float, default=321.6,  help='min. z value start of EE at V10')
    parser.add_option('', '--zMax',  dest='zMax',  type=float, default=650.0,    help='max. z value')
    parser.add_option('', '--rMin',  dest='rMin',  type=float, default=0.0,  help='min. r value')
    parser.add_option('', '--rMax',  dest='rMax',  type=float, default=300.0,    help='max. r value')
    parser.add_option('', '--nopointing',  action='store_false',  dest='pointing',  default=True,    help='produce particles parallel to the beampipe instead of pointing to (0,0,0) in case of closeby gun')
    parser.add_option('', '--overlapping',  action='store_true',  dest='overlapping',  default=False,    help='particles will be generated in window [phiMin,phiMax], [rMin,rMax] (true) or with a DeltaPhi=Delta/R (default false) in case of closeby gun')
    parser.add_option('', '--randomShoot',  action='store_true',  dest='randomShoot',  default=False,    help='if true it will randomly choose one particle in the range [1, NParticles +1 ]')
    parser.add_option('', '--nRandomPart',  dest='NRANDOMPART',  type=int,   default=1,      help='This is used together with randomShoot to shoot randomly [1, NParticles +1 ] particles, default is 1')
    parser.add_option('', '--gunMode',   dest='gunMode',   type='string', default='default',    help='default, pythia8, physproc or closeby')
    parser.add_option('', '--gunType',   dest='gunType',   type='string', default='Pt',    help='Pt or E gun, or in case of gunType physproc details on the physics process')
    parser.add_option('', '--InConeID', dest='InConeID',   type='string',     default='', help='PDG ID for single particle to be generated in the cone (supported as PARTID), default is empty string (none)')
    parser.add_option('', '--MinDeltaR',  dest='MinDeltaR',  type=float, default=0.3, help='min. DR value')
    parser.add_option('', '--MaxDeltaR',  dest='MaxDeltaR',  type=float, default=0.4, help='max. DR value')
    parser.add_option('', '--Delta',  dest='Delta',  type=float, default=0.25, help=' arc-distance between two consecutive vertices over the circle of radius R')
    parser.add_option('', '--MinMomRatio',  dest='MinMomRatio',  type=float, default=0.5, help='min. momentum ratio for particle inside of the cone and particle that defines the cone')
    parser.add_option('', '--MaxMomRatio',  dest='MaxMomRatio',  type=float, default=2.0, help='max. momentum ratio for particle inside of the cone and particle that defines the cone')
    parser.add_option('-l', '--local',  action='store_true', dest='LOCAL',  default=False, help='store output dir locally instead of at EOS CMG area, default is False.')
    parser.add_option('-y', '--dry-run', action='store_true', dest='DRYRUN', default=False, help='perform a dry run (no jobs are lauched).')
    parser.add_option('', '--eosArea', dest='eosArea', type='string', default='/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production', help='path to the eos area where the output jobs will be staged out')
    parser.add_option('-d', '--datTier', dest='DTIER',  type='string', default='GSD', help='data tier to run: "GSD" (GEN-SIM-DIGI) or "RECO", default is "GSD"')
    parser.add_option('-i', '--inDir',  dest='inDir',  type='string', default='',   help='name of the previous stage dir (relative to the local submission or "eosArea"), to be used as the input for next stage, not applicable for GEN stage')
    parser.add_option('-o', '--outDir',  dest='outDir',  type='string', default='',   help='name of the output directory, the default value depends on the data tier and handles duplicate collisions')
    parser.add_option('-r', '--RelVal',  dest='RELVAL',  type='string', default='',   help='name of relval reco dataset to be ntuplized (currently implemented only for NTUP data Tier')
    parser.add_option('', '--noReClust',  action='store_false', dest='RECLUST',  default=True, help='do not re-run RECO-level clustering at NTUP step, default is True (do re-run the clustering).')
    parser.add_option('', '--addGenOrigin',    action='store_true', dest='ADDGENORIG',  default=False, help='add coordinates of the origin vertex for gen particles as well as the mother particle index')
    parser.add_option('', '--addGenExtrapol',  action='store_true', dest='ADDGENEXTR',  default=False, help='add coordinates for the position of each gen particle extrapolated to the first HGCal layer (takes into account magnetic field)')
    parser.add_option('', '--storePFCandidates',  action='store_true', dest='storePFCandidates',  default=False, help='store PFCandidates collection')
    parser.add_option('', '--multiClusterTag',  action='store', dest='MULTICLUSTAG', default="hgcalMultiClusters", help='name of HGCalMultiCluster InputTag - use hgcalLayerClusters before CMSSW_10_3_X')
    parser.add_option('', '--keepDQMfile',  action='store_true', dest='DQM',  default=False, help='store the DQM file in relevant folder locally or in EOS, default is False.')
    parser.add_option('', '--requestGPUs',  action='store_true', dest='GPU',  default=False, help='if used then it is set to True and will use in condor GPU machines, default is False. Keep in mind that GPU machines are limited in contrary to CPU.')

    return parser


### parsing input options
def parseOptions(parser=None, opt=None):
    if not parser:
        parser = createParser()
    if not opt:
        opt, _ = parser.parse_args()

    # sanity check for data tiers
    dataTiers = ['GSD', 'RECO', 'NTUP','ALL']
    if opt.DTIER not in dataTiers:
        parser.error('Data tier ' + opt.DTIER + ' is not supported. Exiting...')
        sys.exit()

    # make sure CMSSW is set up
    if 'CMSSW_BASE' not in os.environ:
        print 'ERROR: CMSSW does not seem to be set up. Exiting...'
        sys.exit()

    partGunModes = ['default', 'pythia8', 'closeby', 'physproc']
    if opt.gunMode not in partGunModes:
        parser.error('Particle gun mode ' + opt.gunMode + ' is not supported. Exiting...')
        sys.exit()

    partGunTypes = ['Pt', 'E']
    if opt.gunMode in ['default', 'pythia8'] and opt.gunType not in partGunTypes:
        parser.error('Particle gun type ' + opt.gunType + ' is not supported. Exiting...')
        sys.exit()

    # Set upper threshold to lower value if upper one not set
    if opt.thresholdMax < 0:
        opt.thresholdMax = opt.thresholdMin

    # set the default config, if not specified in options
    if (opt.CONFIGFILE == '' and opt.DTIER != 'ALL'):
        opt.CONFIGFILE = 'templates/partGun_'+opt.DTIER+'_template.py'
    else:
        opt.CONFIGFILE = 'templates/partGun_GSD_template.py'

    # supported queues with the recommended number of events per hour (e.g. ~4events/1nh for GSD, ~8events/1nh for RECO) + sanity check
    eventsPerHour = {'GSD':4, 'RECO':8, 'NTUP':100, 'ALL':4}
    queues_evtsperjob = {'nextweek':(7*24*eventsPerHour[opt.DTIER]), 'testmatch':(2*24*eventsPerHour[opt.DTIER]), 'tomorrow':(1*24*eventsPerHour[opt.DTIER]), 'workday':(8*eventsPerHour[opt.DTIER]), 'longlunch':(1*eventsPerHour[opt.DTIER]), 'microcentury':(1*eventsPerHour[opt.DTIER]), 'espresso':(1)}
    if opt.QUEUE not in queues_evtsperjob.keys():
        parser.error('Queue ' + opt.QUEUE + ' is not supported. Exiting...')
        sys.exit()
    else:
        if opt.EVTSPERJOB==-1:
            opt.EVTSPERJOB = queues_evtsperjob[opt.QUEUE] # set the recommnded number of events per job, if requested

    # list of supported particles, check if requested partID list is a subset of the list of the supported ones
    particles = ['22', '111', '211', '-211', '11', '-11', '13', '-13', '15', '-15', '12', '14', '16', '130', '1', '-1', '2', '-2', '3', '-3', '4', '-4', '5', '-5', '21']
    inPartID = [p.strip(" ") for p in opt.PARTID.split(",")] # prepare list of requested IDs (split by ",", strip white spaces)
    if not (set(inPartID) < set(particles) or opt.PARTID == ''):
        parser.error('Particle(s) with ID(s) ' + opt.PARTID + ' is not supported. Exiting...')
        sys.exit()

    # sanity check for generation of particle within the cone (require to be compatibe with NPART==1, gunType==Pt and supported particles)
    if (opt.InConeID != '') and (opt.InConeID not in particles):
        parser.error('InCone particle with ID {} is not supported. Exiting...'.format(opt.InConeID))
        sys.exit()
    if (opt.InConeID != '') and (opt.NPART != 1 or opt.gunType != 'Pt'):
        parser.error('In-cone multi-particle gun is incompatible with options NPART = {} (must be 1) or with gunType = {} (gun-type must be Pt). Exiting...'.format(opt.NPART, opt.gunType))
        sys.exit()

    # overwrite for RelVal
    if opt.RELVAL != '':
        particles = ['dummy']

    return opt


### processing the external os commands
def processCmd(cmd, quite = 0):
    #print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
    return output

### print the setup
def printSetup(opt, CMSSW_BASE, CMSSW_VERSION, SCRAM_ARCH, currentDir, outDir):
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
    if opt.gunMode == 'physproc':
        print 'INPUTS:     ', [curr_input, 'Physics process config: ' + ' '.join(opt.gunMode.split(':')),opt.RELVAL][int(opt.DTIER=='GSD')]
    else:
        print 'INPUTS:     ', [curr_input, 'Particle gun mode: ' + opt.gunMode + ', type: ' + opt.gunType + ', PDG ID(s) '+str(opt.PARTID)+', '+str(opt.NPART)+' times per event, ' + opt.gunType + ' threshold in ['+str(opt.thresholdMin)+','+str(opt.thresholdMax)+'], eta threshold in ['+str(opt.etaMin)+','+str(opt.etaMax)+']',opt.RELVAL][int(opt.DTIER=='GSD')]
    if (opt.InConeID!='' and opt.DTIER=='GSD'):
        print '             IN-CONE: PDG ID '+str(opt.InConeID)+', deltaR in ['+str(opt.MinDeltaR)+ ','+str(opt.MaxDeltaR)+']'+', momentum ratio in ['+str(opt.MinMomRatio)+ ','+str(opt.MaxMomRatio)+']'
    if (opt.gunMode == 'closeby' and opt.DTIER=='GSD'):
        print '             z threshold in ['+str(opt.zMin)+','+str(opt.zMax)+'], r threshold in ['+str(opt.rMin)+','+str(opt.rMax)+'], pointing to (0,0,0) '+str(opt.pointing) + ', overlapping '+str(opt.overlapping)+ ', randomShoot '+str(opt.randomShoot) + ', nRandomPart '+str(opt.NRANDOMPART)
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
def submitHGCalProduction(*args, **kwargs):
    opt = parseOptions(*args, **kwargs)

    # save working dir
    currentDir = os.getcwd()
    CMSSW_BASE = os.getenv('CMSSW_BASE')
    CMSSW_VERSION = os.getenv('CMSSW_VERSION')
    SCRAM_ARCH = os.getenv('SCRAM_ARCH')
    commonFileNamePrefix = opt.gunMode
    partGunType = 'FlatRandom%sGunProducer' % opt.gunType
    if opt.gunMode == 'pythia8':
        partGunType = 'Pythia8%sGun' % opt.gunType
    if opt.gunMode == 'physproc':
        partGunType = opt.gunType
    if opt.InConeID != '':
        partGunType = 'MultiParticleInConeGunProducer'  # change part gun type if needed, keep opt.gunType unchanged (E or Pt) for the "primary particle"
    if opt.gunMode == 'closeby':
        partGunType = 'CloseByParticleGunProducer'

    # RELVAL
    DASquery=False
    if opt.RELVAL != '':
        DASquery=True


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
    if opt.outDir:
        outDir = opt.outDir
    elif (opt.DTIER == 'GSD' or opt.DTIER == 'ALL' ):
        outDir = "_".join([partGunType, tag]).replace(":", "_")
        if (not os.path.isdir(outDir)):
            processCmd('mkdir -p '+outDir+'/cfg/')
            processCmd('mkdir -p '+outDir+'/std/')
            processCmd('mkdir -p '+outDir+'/jobs/')
        else:
            print 'Directory '+outDir+' already exists. Exiting...'
            sys.exit()
    elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        if not DASquery:
            # If tag provided, append it to the output directory.
            # This is e.g. useful for running different kinds of
            # reconstruction code on the same input file.
            if opt.TAG:
                outDir = opt.inDir.strip("/") + "_" + opt.TAG
            else:
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
        recoInputPrefix = 'file:'+currentDir+'/'+opt.inDir+'/'+previousDataTier+'/'
        if (opt.DQM): processCmd('mkdir -p '+outDir+'/DQM/')
    elif opt.eosArea:
        if opt.DTIER != 'ALL':
            processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/'+opt.DTIER+'/');
        else:
            processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/NTUP/');
        recoInputPrefix = 'root://eoscms.cern.ch/'+opt.eosArea+'/'+opt.inDir+'/'+previousDataTier+'/'
        if (opt.DQM): processCmd(eosExec + ' mkdir -p '+opt.eosArea+'/'+outDir+'/DQM/')
    # in case of relval always take reconInput from /store...
    if DASquery: recoInputPrefix=''

    # determine number of jobs for GSD, in case of 'RECO'/'NTUP' only get the input GSD/RECO path
    if (opt.DTIER == 'GSD' or opt.DTIER == 'ALL'):
        njobs = int(math.ceil(float(opt.NEVTS)/float(opt.EVTSPERJOB)))
    elif (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        inPath = [opt.eosArea+'/'+opt.inDir, currentDir+'/'+opt.inDir][opt.LOCAL]
        if DASquery: inPath=opt.RELVAL

    # print out some info
    printSetup(opt, CMSSW_BASE, CMSSW_VERSION, SCRAM_ARCH, currentDir, outDir)

    # submit all the jobs
    print '[Submitting jobs]'
    jobCount=0

    # read the template file in a single string
    f_template= open(opt.CONFIGFILE, 'r')
    template=f_template.read()
    f_template.close()


    if (opt.DTIER == 'ALL'):

        cfgfile = opt.CONFIGFILE

        cfgfile = cfgfile.replace('GSD','RECO')
        fr_template= open(cfgfile, 'r')
        r_template=fr_template.read()
        fr_template.close()

        cfgfile = cfgfile.replace('RECO','NTUP')
        fn_template= open(cfgfile, 'r')
        n_template=fn_template.read()
        fn_template.close()

    created_cfgs = []

    nFilesPerJob = 0
    eventsPerPrevJob = 0
    sParticle = [p.strip(" ") for p in opt.PARTID.split(",")]
    processDetails = '_PDGid'+'_id'.join(sParticle)
    if opt.gunMode == 'physproc':
        processDetails = '_'.join(opt.gunType.split(':'))
    cutsApplied = '_'+ '_'.join(opt.gunType.split(':')) + str(opt.thresholdMin) + 'To' + str(opt.thresholdMax) + '_'
    # in case of 'RECO' or 'NTUP', get the input file list for given particle, determine number of jobs, get also basic GSD/RECO info
    if (opt.DTIER == 'RECO' or opt.DTIER == 'NTUP'):
        inputFilesList = getInputFileList(DASquery, inPath, previousDataTier, opt.LOCAL, '*.root')
        if len(inputFilesList) == 0:
            print 'Empty list of input files!'
            return created_cfgs
        # Determine prefix for regex from first input file name
        commonFileNamePrefix = inputFilesList[0].split("_", 1)[0]
        # build regular expression for splitting (NOTE: none of this is used for relval!)
        if not DASquery:
            regex = re.compile(ur"{prefix}(_\S*)_x([0-9]*)(_\S*){tier}_([0-9]*).root".format(prefix=commonFileNamePrefix, tier=previousDataTier))
            matches = regex.match(inputFilesList[0])
            processDetails = matches.group(1)
            eventsPerPrevJob = int(matches.group(2))
            cutsApplied = matches.group(3)  # includes leading and trailing underscore if applicable
            nFilesPerJob = max(int(math.floor(float(min(opt.EVTSPERJOB, len(inputFilesList)*eventsPerPrevJob))/float(eventsPerPrevJob))),1)
            njobs = int(math.ceil(float(len(inputFilesList))/float(nFilesPerJob)))
        else:
            njobs=len(inputFilesList)
            nFilesPerJob = 1

    for job in range(1,int(njobs)+1):
        submittxt = ' for particle ID(s) ' + opt.PARTID
        if DASquery : submittxt=' for RelVal:'+opt.RELVAL
        print 'Submitting job ' + str(job) + ' out of ' + str(njobs) + submittxt

        # prepare the out file and cfg file by replacing DUMMY entries according to input options

        dtier = opt.DTIER
        if dtier == 'ALL':
            dtier = 'GSD'
        if DASquery:
            basename=outDir+'_'+dtier+'_'+str(job)
        else:
            basename = commonFileNamePrefix + processDetails+'_x' + str([nFilesPerJob * eventsPerPrevJob, opt.EVTSPERJOB][opt.DTIER=='GSD']) + cutsApplied + dtier + '_' + str(job)

        cfgfile = basename +'.py'
        outfile = basename +'.root'
        outdqmfile = basename.replace(dtier, 'DQM') +'.root'
        jobfile = basename +'.sub'

        s_template=template

        s_template=s_template.replace('DUMMYFILENAME',outfile)
        s_template=s_template.replace('DUMMYDQMFILENAME',outdqmfile)
        s_template=s_template.replace('DUMMYSEED',str(job))

        if (opt.DTIER == 'GSD' or opt.DTIER == 'ALL' ):
            # in case of InCone generation of particles
            if opt.InConeID != '':
                s_template=s_template.replace('#DUMMYINCONESECTION',InConeSECTION)

            # prepare GEN-SIM-DIGI inputs
            nParticles = ','.join([opt.PARTID for i in range(0,opt.NPART)])
            s_template=s_template.replace('DUMMYEVTSPERJOB',str(opt.EVTSPERJOB))

            s_template=s_template.replace('DUMMYIDs',nParticles)
            s_template=s_template.replace('DUMMYTHRESHMIN',str(opt.thresholdMin))
            s_template=s_template.replace('DUMMYTHRESHMAX',str(opt.thresholdMax))
            s_template=s_template.replace('DUMMYETAMIN',str(opt.etaMin))
            s_template=s_template.replace('DUMMYETAMAX',str(opt.etaMax))
            s_template=s_template.replace('GUNPRODUCERTYPE',str(partGunType))
            if opt.gunMode != 'physproc':
                s_template=s_template.replace('MAXTHRESHSTRING',"Max"+str(opt.gunType))
                s_template=s_template.replace('MINTHRESHSTRING',"Min"+str(opt.gunType))
            s_template=s_template.replace('GUNMODE',str(opt.gunMode))
            if opt.gunMode == 'closeby':
                s_template=s_template.replace('DUMMYZMIN',str(opt.zMin))
                s_template=s_template.replace('DUMMYZMAX',str(opt.zMax))
                s_template=s_template.replace('DUMMYDELTA',str(opt.Delta))
                s_template=s_template.replace('DUMMYRMIN',str(opt.rMin))
                s_template=s_template.replace('DUMMYRMAX',str(opt.rMax))
                s_template=s_template.replace('DUMMYPOINTING',str(opt.pointing))
                s_template=s_template.replace('DUMMYOVERLAPPING',str(opt.overlapping))
                s_template=s_template.replace('DUMMYRANDOMSHOOT',str(opt.randomShoot))
                s_template=s_template.replace('DUMMYNRANDOMPARTICLES',str(opt.NRANDOMPART))

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

        if (opt.DTIER == 'ALL'):

            sr_template=r_template
            sn_template=n_template

            sr_template=sr_template.replace('DUMMYINPUTFILELIST',"'file:"+outfile+"'")
            outfile = outfile.replace('GSD','RECO')

            sr_template=sr_template.replace('DUMMYFILENAME',outfile)
            sr_template=sr_template.replace('DUMMYDQMFILENAME',outdqmfile)
            sr_template=sr_template.replace('DUMMYSEED',str(job))
            sr_template=sr_template.replace('DUMMYINPUTFILELIST',outfile)
            sr_template=sr_template.replace('DUMMYEVTSPERJOB',str(-1))

            sn_template=sn_template.replace('DUMMYINPUTFILELIST',"'file:"+outfile+"'")
            outfile = outfile.replace('RECO','NTUP')
            sn_template=sn_template.replace('DUMMYFILENAME',outfile)
            sn_template=sn_template.replace('DUMMYDQMFILENAME',outdqmfile)
            sn_template=sn_template.replace('DUMMYSEED',str(job))
            sn_template=sn_template.replace('DUMMYEVTSPERJOB',str(-1))

            sn_template=sn_template.replace('DUMMYRECLUST',str(opt.RECLUST))
            sn_template=sn_template.replace('DUMMYSGO',str(opt.ADDGENORIG))
            sn_template=sn_template.replace('DUMMYSGE',str(opt.ADDGENEXTR))
            sn_template=sn_template.replace('DUMMYSPFC',str(opt.storePFCandidates))
            sn_template=sn_template.replace('DUMMYMULCLUSTAG', str(opt.MULTICLUSTAG))



        # submit job
        # now write the file from the s_template

        cfgfile_path = outDir + '/cfg/' + cfgfile
        write_template= open(cfgfile_path, 'w')
        write_template.write(s_template)
        write_template.close()

        cfgfiler = 'dummy'
        cfgfilen = 'dummy'

        if (opt.DTIER == 'ALL'):

            cfgfiler = cfgfile.replace('GSD','RECO')
            cfgfiler_path = outDir + '/cfg/' + cfgfiler
            write_template= open(cfgfiler_path, 'w')
            write_template.write(sr_template)

            cfgfilen = cfgfile.replace('GSD','NTUP')
            cfgfilen_path = outDir + '/cfg/' + cfgfilen
            write_template= open(cfgfilen_path, 'w')
            write_template.write(sn_template)

        write_condorjob= open(outDir+'/jobs/'+jobfile, 'w')
        write_condorjob.write('+JobFlavour = "'+opt.QUEUE+'" \n\n')
        write_condorjob.write('executable  = '+currentDir+'/SubmitFileGSD.sh \n')
        write_condorjob.write('arguments   = $(ClusterID) $(ProcId) '+currentDir+' '+outDir+' '+cfgfile+' '+cfgfiler+' '+cfgfilen+' '+str(opt.LOCAL)+' '+CMSSW_VERSION+' '+CMSSW_BASE+' '+SCRAM_ARCH+' '+opt.eosArea+' '+opt.DTIER+' '+str(opt.DQM)+'\n')

        write_condorjob.write('output      = '+outDir+'/std/'+basename+'.out \n')
        write_condorjob.write('error       = '+outDir+'/std/'+basename+'.err \n')
        write_condorjob.write('log         = '+outDir+'/std/'+basename+'_htc.log \n\n')
        if (opt.GPU): write_condorjob.write('request_GPUs = 1\n') 
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
        created_cfgs.append(cfgfile_path)

    print '[Submitted '+str(jobCount)+' jobs]'

    return created_cfgs

### run the submitHGCalProduction() as main
if __name__ == "__main__":
    submitHGCalProduction()
