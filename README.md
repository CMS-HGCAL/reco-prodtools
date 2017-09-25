# reco-prodtools
Home of the tools to produce samples for HGCAL reconstruction studies

## hello world

Set up CMSSW according to https://github.com/CMS-HGCAL/reco-ntuples

Then anywhere,
```
git clone git@github.com:CMS-HGCAL/reco-prodtools.git
cd reco-prodtools
python SubmitHGCalPGun.py --nevts 2 --evtsperjob 1 --queue 1nh --partID 13 --thresholdMin 35 --thresholdMax 35 --gunType E --tag test_${USER}
```

## details

To produce `NEVENTS` GEN-SIM-DIGI events with `NPART` sets of particles (per event) of type `PART_PDGID` and in the p_T range from `PTMIN` to `PTMAX`, one should run:
```
  python SubmitHGCalPGun.py
  --datTier GSD
  --nevts NEVENTS
  --evtsperjob NPERJOB
  --queue QUEUENAME
  --partID PART_PDGID
  --nPart NPART
  --thresholdMin PTMIN
  --thresholdMax PTMAX
  --gunType GUNTYPE
  [--gunMode GUNMODE]
  [--local]
  --tag MYTAG
```
Here, one can produce a custom set of particles by providing `PART_PDGID` as a set of comma-separated single PDG IDs. To simulate the decay of unstable particles, e.g. quarks, gluons or taus,  an alternative particle gun based on PYTHIA8 can be used by setting `--gunMode pythia8`. 

To produce `NEVENTS` GEN-SIM-DIGI events with pair of particles within given angular distance ΔR(η,φ) (per event), where the first particle is of type `PART_PDGID` and in the p_T range from `PTMIN` to `PTMAX`, and the second one is of type `INCONE_PART_PDGID` and at distance from `DRMIN` to `DRMAX` and with p_T in range from `PTRATIO_MIN` to `PTRATIO_MAX` relative to the first particle, one should run:
```
  python SubmitHGCalPGun.py
  --datTier GSD
  --nevts NEVENTS
  --evtsperjob NPERJOB
  --queue QUEUENAME
  --partID PART_PDGID
  --nPart 1
  --thresholdMin PTMIN
  --thresholdMax PTMAX
  --gunType Pt
  [--gunMode GUNMODE]
  --InConeID INCONE_PART_PDGID
  --MinDeltaR DRMIN
  --MaxDeltaR DRMAX
  --MinMomRatio PTRATIO_MIN
  --MaxMomRatio PTRATIO_MAX
  [--local]
  --tag MYTAG
```
One should also note that for the genertion of pairs of particles within a given cone, one has to use the "Pt" gun. Also note that it is currently not possible to generate pairs within a cone using the PYTHIA8-based gun.

The script will create a directory called `partGun_[MYTAG]_[DATE]` locally or on the CMG EOS area (see options), and submit jobs to queue `QUEUENAME` with `NPERJOB` events per job,
`NEVENTS` in total.
The batch `stdout`/`stderr` files and `.cfg` files used to run
are stored locally `in partGun_[MYTAG]_[DATE]`, while the resulting files `partGun_*_GSD_{i}.root` are stored in `partGun_[MYTAG]_[DATE]` either locally or in  `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.

Rule of thumb for GEN-SIM-DIGI: 4 events per `1nh`:
 * 20 events should be possible to finish in queue `8nh`.
 * Ditto, 100 events in `1nd`.
 
## Include PU at the GSD level
Add options --PU NPUevents --PUDS MinBias_dataset. Remember to 'voms-proxy-init' before so to let the script use das-client. 
Example of MinBias dataset to use: [/MinBias_TuneCUETP8M1_14TeV-pythia8/PhaseIITDRSpring17GS-91X_upgrade2023_realistic_v2-v1/GEN-SIM](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2FMinBias_TuneCUETP8M1_14TeV-pythia8%2FPhaseIITDRSpring17GS-91X_upgrade2023_realistic_v2-v1%2FGEN-SIM)


## RECO step

To run RECO stage on the produced GEN-SIM-DIGI samples, stored under `partGun_[MYTAG]_[DATE]` (locally or on the CMG EOS area), one should run:
```
python SubmitHGCalPGun.py \
  --datTier RECO \
  --evtsperjob NPERJOB \
  --queue QUEUENAME \
  --inDir partGun_[MYTAG]_[DATE] \
  [--local] \
  --tag MYTAG
```

The script will get the list of GEN-SIM-DIGI files from the directory `partGun_[MYTAG]_[DATE]`/`GSD` (locally or on the CMG EOS area), and submit jobs to queue `QUEUENAME` (if possbile with `NPERJOB` events per job).
The batch `stdout`/`stderr` files and `.cfg` files are stored locally `in partGun_[MYTAG]_[DATE]`, while the resulting files `partGun_*_RECO_{i}.root` are stored in `partGun_[MYTAG]_[DATE]`/`RECO` either locally or in  `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.

Rule of thumb for RECO: 10 events per `1nh`:
* 50 events should be possible to finish in queue `8nh`.
* Ditto, 1000 events in `1nd`.


For more info on available options type `python SubmitHGCalPGun.py --help`

## NTUP step

This needs the ntupliser to be installed as in https://github.com/CMS-HGCAL/reco-ntuples

To run NTUP stage on the produced RECO samples, stored under `partGun_[MYTAG]_[DATE]` (locally or on the CMG EOS area), one should run:
```
python SubmitHGCalPGun.py \
  --datTier NTUP \
  --evtsperjob NPERJOB \
  --queue QUEUENAME \
  --inDir partGun_[MYTAG]_[DATE] \
  [--noReClust] \
  [--local] \
  --tag MYTAG
```
## RelVal

It can also run directly on RelVal using the same NTUP cfg. It runs das_client internally so you need to have a valid proxy (i.e. run voms-proxy-init before). The output goes in an area (eos/local) named after the RelVal dataset with all '/' replaced by underscores.

Typical usage:
```
python SubmitHGCalPGun.py \
  --datTier NTUP \
  --queue QUEUENAME \
  [--local] \
  -r /RelValSingleMu..etc.
```


# to contribute

We use the _fork and pull_ model:

[Fork this repository](https://github.com/CMS-HGCAL/reco-prodtools/fork).

If you haven't done so yet, clone this repository:
```
git clone git@github.com:CMS-HGCAL/reco-prodtools.git
```
Add your fork of the repository as remote:
```
git remote add mine git@github.com:`git config user.github`/reco-prodtools.git
git checkout -b ${USER}_feature_branch origin/master
```
Work on your feature, `add`, `commit`, etc.
```
git fetch origin
git rebase origin/master
git push mine feature_branch
```

 Make a pull request on github.
