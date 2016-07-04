    # reco-prodtools
Home of the tools to produce samples for HGCAL reconstruction studies

## hello world

Setup a `CMSSW_8_1_0_pre7` (`slc6_amd64_gcc530`) according to
https://github.com/CMS-HGCAL/cmssw

Then anywhere,
```
git clone https://github.com/CMS-HGCAL/reco-prodtools.git
cd reco-prodtools
python SubmitHGCalPGun.py --nevts 2 --evtsperjob 1 --queue 1nh --partID 13 --pTmin 34.9 --pTmax 35.1 --tag test_${USER}
```

## details

To produce `NEVENTS` GEN-SIM-DIGI events with `NPART` particles (per event) of type `PART_PDGID` and in the p_T range from `PTMIN` to `PTMAX`, one should run:
```
  python SubmitHGCalPGun.py
  --datTier GSD
  --nevts NEVENTS
  --evtsperjob NPERJOB
  --queue QUEUENAME
  --partID PART_PDGID
  --nPart NPART
  --pTmin PTMIN
  --pTmax PTMAX
  [--local]
  --tag MYTAG
```

The script will create a directory called `partGun_[MYTAG]_[DATE]` locally or on the CMG EOS area (see options), and submit jobs to queue `QUEUENAME` with `NPERJOB` events per job,
`NEVENTS` in total.
The batch `stdout`/`stderr` files and `.cfg` files used to run
are stored locally `in partGun_[MYTAG]_[DATE]`, while the resulting files `partGun_*_GSD_{i}.root` are stored in `partGun_[MYTAG]_[DATE]` either locally or in  `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.

Rule of thumb for GEN-SIM-DIGI: 4 events per `1nh`:
 * 20 events should be possible to finish in queue `8nh`.
 * Ditto, 100 events in `1nd`.

To run RECO stage on the produced GEN-SIM-DIGI samples, stored under `partGun_[MYTAG]_[DATE]` (locally or on the CMG EOS area), one should run:
```
python SubmitHGCalPGun.py
  --datTier RECO
  --evtsperjob NPERJOB
  --queue QUEUENAME
  --inDir partGun_[MYTAG]_[DATE]
  [--local]
  --tag MYTAG
```

The script will get the list of GEN-SIM-DIGI files from the directory `partGun_[MYTAG]_[DATE]`/`GSD` (locally or on the CMG EOS area), and submit jobs to queue `QUEUENAME` (if possbile with `NPERJOB` events per job).
The batch `stdout`/`stderr` files and `.cfg` files are stored locally `in partGun_[MYTAG]_[DATE]`, while the resulting files `partGun_*_RECO_{i}.root` are stored in `partGun_[MYTAG]_[DATE]`/`RECO` either locally or in  `/eos/cms/store/cmst3/group/hgcal/CMG_studies/Production/`.

Rule of thumb for RECO: 10 events per `1nh`:
* 50 events should be possible to finish in queue `8nh`.
* Ditto, 1000 events in `1nd`.


For more info on available options type `python SubmitHGCalPGun.py --help`

# to contribute

We use the _fork and pull_ model:

[Fork this repository](https://github.com/CMS-HGCAL/reco-prodtools/fork).
```
git clone https://github.com/${USER}/reco-prodtools.git
git remote add upstream https://github.com/CMS-HGCAL/reco-prodtools.git
git checkout -b ${USER}_feature_branch upstream/master
```
Work on your feature, `add`, `commit`, etc.
```
git fetch upstream
git rebase upstream/master
git push origin ${USER}_feature_branch
```

 Make a pull request on github.
