# MIT License
# 
# Copyright (c) 2018 Michael DeFelice
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urllib.request
import os
import glob
import zipfile

import numpy as np, pandas as pd
import matplotlib.pyplot as plt
plt.style.use ('seaborn-paper')

from matplotlib.ticker import FuncFormatter

# Function to generate plots
def gen_na_plots (df, _nam = 'Rebecca', _sex = 'F'):
    dm = pd.read_csv ('~/ds/DeathProbsE_{}_Alt2_TR2014.csv'.format (_sex), skiprows = 1)
    a = dm.set_index ('Year').loc[pd.to_datetime ('now').year].rename ('pd')
    a.index = a.index.astype ('int64')
    a.index.name = 'age'

    b = df[(df.sex == _sex) & (df.name == _nam)].groupby (['age']).n.sum ()

    c = pd.concat ([
        b,
        a,
    ], axis = 1).dropna ()

    c['pl'] = 1 - c.pd
    c['plc'] = c.pl.cumprod ()
    c['adj'] = (c.n * c.plc)
    c['by'] = pd.to_datetime ('now').year - c.index
    c['adjc'] = c.adj.cumsum ()

    m = c[c.adjc >= c.adjc.max () / 2].iloc[0].name
    d = c[['n', 'adj']]
    d.index.name = ''

    fig, ax = plt.subplots (1, 1, figsize = (8, 5))
    d.n.rename ('Born').plot (title = '{}: US Age Distribution'.format (_nam))
    d.adj.rename ('Expected Living (2017)').plot (kind = 'area', title = '{}: US Age Distribution'.format (_nam))
    plt.axvline (x = m, c = 'k', ls = ':', lw = 0.8)
    ax.set_xlim (0, 100)
    ax.get_yaxis ().set_major_formatter (FuncFormatter (lambda a, b: '{:,.0f}K'.format (a * 1e-3)))
    ax.annotate ('{:.0f}'.format (m), xy = (m, 0), xycoords = 'data', xytext = (0, 4), textcoords = 'offset points', ha = 'center', va = 'center', size = 8, weight = 'bold', bbox = {'fc': 'white', 'ec': 'white', 'pad': 4, 'alpha': 1})
    plt.legend (frameon = 0)
    plt.savefig ('na-{}.pdf'.format (_nam.lower ()))
    plt.close ()


if __name__ == '__main__':
    # Download data sources from ssa.gov ... first ensure directory ~/ds exists
    if not os.path.exists ('ds'):
        os.makedirs ('ds')

    for _ in [
        'https://www.ssa.gov/oact/babynames/state/namesbystate.zip',
        'https://www.ssa.gov/oact/HistEst/Death/2014/DeathProbsE_F_Alt2_TR2014.csv',
        'https://www.ssa.gov/oact/HistEst/Death/2014/DeathProbsE_M_Alt2_TR2014.csv',
    ]:
        if not os.path.isfile ('ds/{}'.format (os.path.basename (_))):
            with urllib.request.urlopen (_) as p, open ('ds/{}'.format (os.path.basename (_)), 'wb') as f:
                f.write (p.read ())

    # Unzip
    for _ in glob.glob (r'ds/*.zip'):
        with zipfile.ZipFile (_, 'r') as z:
            z.extractall ('ds/namesbystate')

    # Create a pandas DataFrame; combine each state's birth records
    df = pd.DataFrame ()
    for _ in glob.glob ('ds/namesbystate/*.TXT'):
        print ('Adding: {}'.format (_))
        a = pd.read_csv (_, header = None, names = ['state', 'sex', 'by', 'name', 'n'])
        df = df.append (a)

    df['age'] = pd.to_datetime ('now').year - df.by

    # Generate plots
    gen_na_plots (df, _nam = 'John', _sex = 'M')
    gen_na_plots (df, _nam = 'Paul', _sex = 'M')
    gen_na_plots (df, _nam = 'Lucy', _sex = 'F')
    gen_na_plots (df, _nam = 'Rita', _sex = 'F')

