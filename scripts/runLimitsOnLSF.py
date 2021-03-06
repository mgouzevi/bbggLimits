#!/usr/bin/env python

from ROOT import *
import os,sys
import getpass
import tempfile
username = getpass.getuser()

# This is a command to run for Analytical reweighted limit:
org_bashFile = '''
#!/bin/bash
cd HERE
eval `scramv1 runtime -sh`
pyLimits.py -f JSONFILE -o LOUTDIR EXTRA --overwrite -j1 -v5 TTHTAGGER
'''

# This is a script for running the limits of grid reweighting
grid_bashFile = '''
#!/bin/bash
workDir=$1
outDir=$2
Point=$3
Json=$4
echo $workDir $outDir $Point
cd $workDir
ls
eval `scramv1 runtime -sh`
pyLimits.py -f $Json -o $outDir --points $Point -j1 -v2 --overwrite
'''

HERE = os.environ['PWD']

import argparse
parser =  argparse.ArgumentParser(description='submit the limit to the batch')
parser.add_argument('-t', '--type', dest="scanType", default=None, type=str, nargs='+',
                    choices=['JHEP', 'KL', 'KLKT', 'grid', 'manual'],
                    help = "Choose the type of limits to run")
parser.add_argument('-f', '--configFile', dest="fname", type=str, default='conf_default.json', required=True,
                    help="Json config file")
parser.add_argument('-o', '--outDir', dest="outDir", type=str, default='LIMS_NewHope',
                    help="Output directory for my limits")
parser.add_argument('--ttHTaggerCut', dest='ttHTaggerCut', type=float, default=None)

opt = parser.parse_args()

def submitPoint(kl=1, kt=1, cg=0, c2=0, c2g=0):
  pointStr = "_".join(['kl',str(float(kl)),'kt',str(float(kt)),'cg',str(float(cg)),'c2',str(float(c2)),'c2g',str(float(c2g))]).replace('.', 'p').replace('-', 'm')
  extra = ' '.join([' --analyticalRW','--kl '+str(kl),'--kt '+str(kt),'--cg '+str(cg),'--c2 '+str(c2), '--c2g '+str(c2g),
                    '--extraLabel '+pointStr])

  bashFile = org_bashFile.replace('HERE', HERE).replace('LOUTDIR', opt.outDir).replace('EXTRA', extra).replace('JSONFILE',opt.fname)
  if opt.ttHTaggerCut!=None:
    bashFile = bashFile.replace('TTHTAGGER', '--ttHTaggerCut '+str(opt.ttHTaggerCut))
  else:
    bashFile = bashFile.replace('TTHTAGGER', '')
    
  with tempfile.NamedTemporaryFile(dir='/tmp/'+username, prefix='batch_LIM_'+pointStr, suffix='.sh', delete=False) as bFile:
    bFile.write(bashFile)
    bFile.flush()
    command = "bsub -q 1nh -J batch_LIM_" + pointStr+ " < " + bFile.name
    print command
    os.system(command)


if __name__ == "__main__":
  print "This is the __main__ part"

  from HiggsAnalysis.bbggLimits.DefineScans import *

  counter = 0
  if "JHEP" in opt.scanType:
    for ii in range(0, len(klJHEP)):
      kl = klJHEP[ii]
      kt = ktJHEP[ii]
      cg = cgJHEP[ii]
      c2 = c2JHEP[ii]
      c2g =c2gJHEP[ii]

      print counter
      counter += 1
      print kl, kt, cg, c2, c2g
      submitPoint(kl, kt, cg, c2, c2g)


  if "KL" in opt.scanType:
    kt = 1.0
    cg = 0.0
    c2 = 0.0
    c2g = 0.0
    for kl in scan_kl['kl']:

      print counter
      counter += 1
      print kl, kt, cg, c2, c2g
      submitPoint(kl, kt, cg, c2, c2g)

  if "KLKT" in opt.scanType:
    cg = 0.0
    c2 = 0.0
    c2g = 0.0
    for kl in scan_2d['kl']:
      for kt in scan_2d['kt']:

        if kt <= 0: continue # Because they are symmetric!

        print counter
        counter += 1
        print kl, kt, cg, c2, c2g
        submitPoint(kl, kt, cg, c2, c2g)


  if 'manual' in opt.scanType:
    # Here we can run limits over specific points
    # Note: the limit trees for those points must exist
    cg = 0.0
    c2 = 0.0
    c2g = 0.0
    kt = 0.0
    kl = 15.5
    submitPoint(kl, kt, cg, c2, c2g)
    #for kl in [1.0, 4.4]:
    #  for kt in [float(i)/(4) for i in range(-10,11)]:
    #    print counter
    #    counter += 1
    #    print kl, kt, cg, c2, c2g
    #    submitPoint(kl, kt, cg, c2, c2g)


  if "grid" in opt.scanType:
    bFile = open('/tmp/'+username+'/batch_grid.sh', "w+")
    bFile.write()
    bFile.close()
    counter = 0
    for j in xrange(0,5):
      command = ' '.join(['bsub -q 1nh','/tmp/'+username+'batch_grid.sh',HERE,'GridLimits', str(j), opt.fname])
      print counter
      counter += 1
      print command
      os.system(command)
