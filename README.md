# reco-prodtools

Home of the tools to produce samples for HGCAL reconstruction studies

## Getting started

Set up CMSSW according to [github.com/CMS-HGCAL/reco-ntuples](https://github.com/CMS-HGCAL/reco-ntuples).

Then anywhere,

```shell
git clone git@github.com:CMS-HGCAL/reco-prodtools.git reco_prodtools
cd reco_prodtools/templates/python
./produceSkeletons_D41_NoSmear_noPU.sh
cd ../../..
scram b
cd reco_prodtools/
python SubmitHGCalPGun.py --nevts 2 --evtsperjob 1 --queue 1nh --partID 13 --thresholdMin 35 --thresholdMax 35 --gunType E --tag test_${USER}
```

Mind that the directory `reco_prodtools` needs to have the underscore (instead of a hyphen).

## Available configurations

For details on the geometry, please see [Configuration/Geometry/README.md](https://github.com/cms-sw/cmssw/blob/master/Configuration/Geometry/README.md)
For details on the pileup scenario, please see [Configuration/StandardSequences/python/Mixing.py](https://github.com/cms-sw/cmssw/blob/master/Configuration/StandardSequences/python/Mixing.py)

| Snippet        | Era            | Geometry       | Beamspot       | PU             |
| -------------- | -------------- | -------------- | -------------- | -------------- |
| [produceSkeletons_D41_NoSmear_noPU.sh](templates/python/produceSkeletons_D41_NoSmear_noPU.sh) | Phase2C8_timing_layer_bar | D41 | NoSmear | none |
| [produceSkeletons_D41_NoSmear_PU_AVE_200_BX_25ns.sh](templates/python/produceSkeletons_D41_NoSmear_PU_AVE_200_BX_25ns.sh) | Phase2C8_timing_layer_bar | D41 | NoSmear | AVE_200_BX_25ns |
| [produceSkeletons_D41_VtxSmearedHLLHC_noPU.sh](templates/python/produceSkeletons_D41_VtxSmearedHLLHC_noPU.sh) | Phase2C8_timing_layer_bar | D41 | VtxSmearedHLLHC | none |

Whenever you would like to change configuration, change to the `reco_prodtools/templates/python` directory and execute the corresponding script. Then make sure to run `scram b`.

## Details

To produce `NEVENTS` GEN-SIM-DIGI events with `NPART` sets of particles (per event) of type `PART_PDGID` and in the p_T range from `PTMIN` to `PTMAX`, one should run:

```shell
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

```shell
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

### Close-by gun

Another gun that could be used is `--gunMode closeby`, which is capable of creating several vertices. Mind that it is only available in `CMSSW_10_6_0` or later.
With this choice particles can be produced with random energy, R and Z in a specified range. When more than
one particle are asked to be produced, then each particle will be created at a different vertex,
equally spaced by Delta, the arc-distance between two consecutive vertices
over the circle of radius R. Also, there is the `--pointing` option which if used particles will be produced parallel to the beamline,  otherwise they will be pointing to (0,0,0). Furthermore, there is the `--overlapping` option that if used then
particles will be generated in a window [phiMin,phiMax], [rMin,rMax], otherwise with a DeltaPhi=Delta/R.
Another option is `--randomShoot` which if used will shoot a random number of particles. However, this option should be used alongside the `--nRandomPart` in order for the gun to know the upper limit on how many particles to shoot. The `--nRandomPart` option shouldn't be confused with the size of the `--partID` option, since with `--partID` we are setting the particles we are interesting in producing, while with `--nRandomPart` we are randomly choosing the number we want to shoot out of those `--partID` ids.
Apart from producing multiple particles, this gun could also produce a single particle wherever the user wishes, having always the
nice feature of assigning to the vertex the time required to travel from (0,0,0) to the desired location. This could be
useful e.g. when someone wants to shoot straight to the scintillator part. Keep in mind that in this case there is no sense of
neither adding the antiparticle nor adding the `--randomShoot` option.
As an example, the command below will produce `NEVENTS` GEN-SIM-DIGI events with `NPART` sets of particles (per event) of type `PART_PDGID`
in the energy range from `EMIN` to `EMAX` (Pt option not available), radius range from `RMIN` to `RMAX`, z position from `ZMIN` to `ZMAX`, parallel to the beamline, with a distance between the particles vertices of deltaPhi = DELTA/R.

```shell
  python SubmitHGCalPGun.py
  --datTier GSD
  --nevts NEVENTS
  --evtsperjob NPERJOB
  --queue QUEUENAME
  --partID PART_PDGID
  --nPart NPART
  --thresholdMin EMIN
  --thresholdMax EMAX
  --rMin RMIN
  --rMax RMAX
  --zMin ZMIN
  --zMax ZMAX
  --Delta DELTA
  --pointing
  --etaMin ETAMIN
  --etaMax ETAMAX
  --gunType E
  --gunMode closeby
  --tag MYTAG
```

### RECO step

To run RECO stage on the produced GEN-SIM-DIGI samples, stored under `partGun_[MYTAG]_[DATE]` (locally or on the CMG EOS area), one should run:

```shell
python SubmitHGCalPGun.py \
  --datTier RECO \
  --evtsperjob NPERJOB \
  --queue QUEUENAME \
  --inDir partGun_[MYTAG]_[DATE] \
  [--local] \
  --tag MYTAG \
  --keepDQMfile
```

The script will get the list of GEN-SIM-DIGI files from the directory `partGun_[MYTAG]_[DATE]`/`GSD` (locally or on the CMG EOS area), and submit jobs to queue `QUEUENAME` (if possbile with `NPERJOB` events per job).
The batch `stdout`/`stderr` files and `.cfg` files are stored locally `in partGun_[MYTAG]_[DATE]`, while the resulting files `partGun_*_RECO_{i}.root` are stored in `partGun_[MYTAG]_[DATE]`/`RECO` either locally or in  `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.
In case the `--keepDQMfile` option is used, the resulting `partGun_*_DQM_{i}.root` files will also be stored in `partGun_[MYTAG]_[DATE]`/`DQM` locally or in `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.

Rule of thumb for RECO: 10 events per `1nh`:

* 50 events should be possible to finish in queue `8nh`.
* Ditto, 1000 events in `1nd`.

For more info on available options type `python SubmitHGCalPGun.py --help`

### NTUP step

This needs the ntupliser to be installed as in [github.com/CMS-HGCAL/reco-ntuples](https://github.com/CMS-HGCAL/reco-ntuples)

To run NTUP stage on the produced RECO samples, stored under `partGun_[MYTAG]_[DATE]` (locally or on the CMG EOS area), one should run:

```shell
python SubmitHGCalPGun.py \
  --datTier NTUP \
  --evtsperjob NPERJOB \
  --queue QUEUENAME \
  --inDir partGun_[MYTAG]_[DATE] \
  [--multiClusterTag hgcalLayerClusters] \
  [--noReClust] \
  [--local] \
  --tag MYTAG
```

Mind that the `multiClusterTag` option needs to be provided for RECO files created before `CMSSW_10_3_X`.

### RelVal

It can also run directly on RelVal using the same NTUP cfg. It runs das_client internally so you need to have a valid proxy (i.e. run voms-proxy-init before). The output goes in an area (eos/local) named after the RelVal dataset with all '/' replaced by underscores.

Typical usage:

```shell
python SubmitHGCalPGun.py \
  --datTier NTUP \
  --queue QUEUENAME \
  [--local] \
  -r /RelValSingleMu..etc.
```

## Notes

Starting from `CMSSW_10_4_0_pre3` (cms-sw/cmssw#25208), the handling of the calibration weights has been rewritten to be more generic and play nicely with eras. PR #54 took care of these changes.

## Updating and adding configurations

To update and add new configurations, you need to pick a geometry as listed in [Configuration/Geometry/README.md](https://github.com/cms-sw/cmssw/blob/master/Configuration/Geometry/README.md), and then run the following command grepping for your desired geometry (here `D41`) and usually also a process of interest (here `SinglePiPt`):

```shell
runTheMatrix.py -w upgrade -n | grep D41 | grep SinglePiPt
```

This will result in output similar to the following:

```shell
20488.0 SinglePiPt25Eta1p7_2p7_2026D41_GenSimHLBeamSpotFull+DigiFullTrigger_2026D41+RecoFullGlobal_2026D41+HARVESTFullGlobal_2026D41
20688.0 SinglePiPt25Eta1p7_2p7_2026D41PU_GenSimHLBeamSpotFull+DigiFullTriggerPU_2026D41PU+RecoFullGlobalPU_2026D41PU+HARVESTFullGlobalPU_2026D41PU
```

In the above case, there are two workflows listed, one with and one without PU. Let's pick the one with PU, `20688.0`, and get the configs:

```shell
runTheMatrix.py -w upgrade -l 20688.0 --command="--no_exec" --dryRun
```

This will run a while and create a new directory that contains the configs (e.g. `20688.0_SinglePiPt25Eta1p7_2p7_2026D41PU_GenSimHLBeamSpotFull+DigiFullTriggerPU_2026D41PU+RecoFullGlobalPU_2026D41PU+HARVESTFullGlobalPU_2026D41PU`). Further, several `cmsDriver.py` scripts will be printed out to the screen. These are the ones that need to be adjusted and put into the corresponding shell scripts (have a look at the existing shell scripts themselves).

Some general guidelines:

* For all commands remove `--filein` and `--fileout` options.
* Add `python_filename` option

The first command combines step1 and step2 (GSD):

* mix in pileup (for 200 PU use e.g. `--pileup AVE_200_BX_25ns`)
* run up to `DIGI...HLT:@fake2`

The following changes are implemented on top/need to be adjusted:

* `--beamspot HLLHC14TeV` ➜ `--beamspot NoSmear` (if you don't want a smeared beamspot)
* `--eventcontent FEVTDEBUG` ➜ `--eventcontent FEVTDEBUGHLT` (since step2 has that)

The second command is step3 removing overlap with step2 (RECO):

* remove pileup part
* also remove `MINIAODSIM`, `PAT`
* remove from `VALIDATION@miniAODValidation`
* remove from `DQM:@miniAODDQM`

The third command is a copy of the second only re-running RECO (for NTUP):

* remove `DQM`
* add `processName=NTUP` option

For more details see the [configuration files listed above](available-configurations).

## Contributing

We use the _fork and pull_ model:

[Fork this repository](https://github.com/CMS-HGCAL/reco-prodtools/fork).

If you haven't done so yet, clone this repository:

```shell
git clone git@github.com:CMS-HGCAL/reco-prodtools.git reco_prodtools
```

Add your fork of the repository as remote:

```shell
git remote add mine git@github.com:`git config user.github`/reco-prodtools.git
git checkout -b ${USER}_feature_branch origin/master
```

Work on your feature, `add`, `commit`, etc.

```shell
git fetch origin
git rebase origin/master
git push mine feature_branch
```

 Make a pull request on github.
