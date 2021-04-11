# -*- coding: utf-8 -*-
# Python 3.7.7
"""
Transform the data from Bailey & GoodmanBacon (2015) to a balanced panel format so that 
the method of Sant'Anna & Zhao (2020) can be applied directly to the transformed data.
"""

import os
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
# Use R-like formulas 
import statsmodels.formula.api as smf
# Desing R-like data tables
from patsy import dmatrices, dmatrix
from statsmodels.iolib.summary2 import summary_col  # summarize regression  tables in a star format




work_dir = r'C:\Users\ropot\OneDrive\Desktop\Spring 2020-21\ECON50580 - PhD Econometrics 2\Replication Exercise - Group 1\Python Code'
os.chdir(work_dir)

# -----------------------------------------------------------------------
#        TRANSFORMATION OF THE MAIN DATASET - aer_data.dta
# -------------------------------------------------------------------

# Import data
data = pd.read_stata(os.path.join(work_dir, 'aer_data.dta'))
# Define the calendar year from the 'year' column
data['cyear'] = pd.to_datetime(data['year']).dt.year
# Define treatment status with the establishment of a CHC
data['treatment'] = (data['cyear']>=data['chc_year_exp']).apply(lambda x: 1 if x == True else 0)


"""
We limit our observations between 1959 and 1980. 
In our analysis, we distinguish 2 periods:
    i) The pre-treatment period that spans 1959-1964 (6 years) --> T=0 
    ii) The post-treatment period that spans 1975-1980 (6 years) --> T=1
    Note: We treat the period 1965-1974 as the time of the treatment, a single 
    moment in time where T=1 holds.

Our sample consists of 2 groups of counties(units):
    i) counties that have been treated (a CHC has been established) between 1965-1974
    ii) counties that have not been treated before 1980. That means the untreated group excludes
    units that have been treated anytime between 1975 and 1980 as this would serve as the 
    comparison group for the treated.
"""


# Limit the sample to the period 1959-1980
data = data[(data['cyear']>= 1959) & (data['cyear']<=1980)]

# Exclude units that have been treated any time between 1975 and 1980
units_ex = list(set(data[(data['exp2'] == 0) & (data['cyear'] >= 1975) & (data['cyear'] <= 1980)]['fips']))
data = data[~data['fips'].isin(units_ex)]

# Fraction of units that get treated by calendar year
# Define change of treatment status = diff(treatment) for each county in our sample
data['change'] = data.sort_values(by = ['fips', 'cyear']).groupby('fips')['treatment'].transform(lambda x: x.diff())
# NaN values of 'change' are replaced by 0 -> no change in status
data = data.fillna(value = {'change':0})
# Calculate the fraction of treated groups over total population each year
treat_frac = data.groupby('cyear').apply(lambda x: x.dropna()['change'].sum() / len(x))
treat_frac.plot(kind = 'bar')
# Cumulative fraction of treated units over time
treat_frac_cum = treat_frac.cumsum()
treat_frac_cum.plot(kind = 'bar')

# Define the pre- and post-treatment period T=0 and T=1 as expected.
# Note: period = -99 for years 1965-1974
data['period'] = data['cyear'].apply(lambda x: 0 if x<= 1964 else ( 1 if x>= 1975 else -99 ))

# Exclude all years between 1965 and 1974
# data = data[(data['cyear']<=1964) | (data['cyear']>=1975)]

# Aggregate relevant variables in Periods T=0 (pre-) and T=1 (post-)

# Old variables - Aggregate all variables except 
vars_ex = ['fips', 'stfips', 'cofips', 'year', 'cyear', 'treatment', 'change', 'period']
vars_old = list(set(data.columns) - set(vars_ex))
# New aggregated variables 
vars_new = [i+'_agg' for i in vars_old]
data[vars_new] = data.groupby(by = ['fips', 'period'])[vars_old].transform(lambda x: x.mean())


# Drop observations that are in 1965-1974 --> T = -99
data = data.drop(index = (data[data['period'] == -99]).index, axis = 0)
# Drop duplicates based for panel data as in Sant'Anna & Zhao
data = data.drop_duplicates(subset = ['fips', 'period'])

# Keep only columns that have been aggregated (suffix = '_agg')
data = data[vars_ex + vars_new]

# Sort dataframe
data = data.sort_values(by = ['fips', 'period'])
# Save the aggregated dataset
data.to_csv(os.path.join(work_dir, 'aer_data_panel.csv'), index = False)

# Null values 
data.isnull().sum().to_csv(os.path.join(work_dir, 'aer_data_panel_null.csv'))


# ----------------------------------------------------------------------------
#    TRANSFORMATION/MERGE OF THE PROPENSITY SCORE DATASET -aer_pscore_data.dta 
# -----------------------------------------------------------------------------

# Import data
ps = pd.read_stata(os.path.join(work_dir, 'aer_pscore_data.dta'))

# Save names of covariates for later usage
covts = list(ps.columns[2:])
# Generate the string for the Sant'Anna formula
xformla_covts = (" + ").join(covts)

# Left merge of main dataset with pscore dataset so that covariates are included
data_ps = pd.merge(data, ps, how = 'left',  on = ['stfips', 'cofips'])
# Impute missing values for each county ('fips') with the mean value by state ('stfips')
covts_st = data_ps.groupby('stfips')[covts].transform(lambda x: x.mean())
data_ps[covts] = data_ps[covts].fillna(value = covts_st)

# Define the "treated" column that is 1 in both periods if the unit is treated and 0 
# otherwise
data_ps['treated'] = data_ps['treatment']
# Find which counties have been treated
units_treat = list(data_ps[data_ps['treatment'] == 1]['fips'])
data_ps.loc[(data_ps['period']==0) & (data_ps['fips'].isin(units_treat) ) ,'treated'] = 1


# sense check
print(data_ps.groupby('fips')['treated'].apply(lambda x: x.diff()).sum())

# -----------------------------------------------------------------------
#                  FINAL MANIPULATIONS
# -------------------------------------------------------------------------

# Remove the underscores from the start of the column names of the covariates 
covts_new = [i[1:] if i[0]=='_' else i for i in covts]
# Create a dictionary to rename the variables 
dict_col = {}
for i in range(len(covts)):
    dict_col[covts[i]] = covts_new[i]
data_ps = data_ps.rename(columns = dict_col)



# --------------------------------------------------------------
#                FINAL DATASET - USED IN APPLICATION
#------------------------------------------------------------------


# No Null values in "amr_agg" and "amr_eld_agg"
data_ps = data_ps.dropna(subset= ['amr_agg', 'amr_eld_agg'])
data_ps.to_csv(os.path.join(work_dir, 'aer_pscore_data_panel_clean.csv'), index = False)

# Generate search string for xformla
xformla = " + ".join(covts_new)
print(xformla)


# ----------------- FINAL DATASET ULTRA CLEANED - NOT USED -------------------
# No Null values in "amr_agg", "amer_eld_agg" and covts_new
data_ps_clean = data_ps.dropna(subset = ['amr_agg', 'amr_eld_agg'] + covts_new)
data_ps_clean.to_csv(os.path.join(work_dir, 'aer_pscore_data_panel_ultra_clean.csv'), index = False)




















