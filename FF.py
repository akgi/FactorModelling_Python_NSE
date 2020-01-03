import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy, scipy.stats

writer = pd.ExcelWriter('df.xlsx', engine='xlsxwriter')
pd.options.mode.chained_assignment = None

nse = pd.read_excel('NSE_FF.xlsx' , sheet_name="Sheet1")
nse.head(10)

dfNew = nse
dfNew['MKtReturn'] = ""
dfNew['MktPrem'] = ""
a = dfNew.Date1.unique()
fileRange = np.arange(0, len(a)-1)  
for i in fileRange:
    print(a[i+1])
    dfNew['MKtReturn'].loc[dfNew['Date1'] == a[i+1]]  = (dfNew['Mkt'].loc[dfNew['Date1'] == a[i+1]].iloc[0] / dfNew['Mkt'].loc[dfNew['Date1'] == a[i]].iloc[0] - 1)*100
    dfNew['MktPrem'].loc[dfNew['Date1'] == a[i+1]] = dfNew['MKtReturn'].loc[dfNew['Date1'] == a[i+1]].iloc[0] - dfNew['RF'].loc[dfNew['Date1'] == a[i+1]].iloc[0]

dfNew['stockreturn'] = ""
tickers = dfNew.SYMBOL.unique()
f = np.arange(0, len(tickers)-1)  
a = dfNew.Date1.unique()
fileRange = np.arange(0, len(a)-1)

for i in f:
    for j in fileRange:
        print(i,j)
        try:
            dfNew['stockreturn'].loc[((dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j]))] = ( dfNew['CLOSE PRICE'].loc[(dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j])].iloc[0] ) / ( dfNew['CLOSE PRICE'].loc[(dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j+1])].iloc[0] )*100-100#/ dfNew['CLOSE PRICE'].loc[(dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j+1])]  -1 )*100
        except:
            pass
df = dfNew

for j in fileRange:
    print(j)
    try:
        df['MKtReturn'].loc[((df['Date1'] == a[j]))] = (df['Mkt'].loc[(df['SYMBOL'] == 'KOTAKNIFTY') & (df['Date1'] == a[j])].iloc[0] ) / (df['Mkt'].loc[(df['SYMBOL'] == 'KOTAKNIFTY') & (df['Date1'] == a[j+1])].iloc[0] )*100-100#/ dfNew['CLOSE PRICE'].loc[(dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j+1])]  -1 )*100
        #df['MKtReturn'].loc[((df['Date1'] == a[j]))] = (df['Mkt'].loc[(df['SYMBOL'] == 'KOTAKNIFTY') & (df['Date1'] == a[j])].iloc[0] ) / (df['Mkt'].loc[(df['SYMBOL'] == 'KOTAKNIFTY') & (df['Date1'] == a[j+1])].iloc[0] )*100-100#/ dfNew['CLOSE PRICE'].loc[(dfNew['SYMBOL'] == tickers[i]) & (dfNew['Date1'] == a[j+1])]  -1 )*100
    except:
        pass

df2=df[~(df['Date1'] == a[-1])]
df2['MktPrem']= df2['MKtReturn'] - df2['RF']
# df2.to_excel('df2.xlsx', header=True, index=False) ###############################

"""
Compute SMB
"""
df=df2
#Define Quantile
SQuantile = 0.3
LQuantile = 0.7
df["SMB"] = ""
df["SMB_f"] = ""
df["SCR"] = ""
#Assigns stock size based on market cap
df.SMB[df.MCAP <= df.MCAP.quantile(SQuantile)] = "SCap"
df.SMB[(df.MCAP > df.MCAP.quantile(SQuantile)) & (df.MCAP < df.MCAP.quantile(LQuantile))] = "MCap"
df.SMB[df.MCAP >= df.MCAP.quantile(LQuantile)] = "LCap"

#Calculates average return of stocks in portfolio subset based on size
b = df.Date1.unique()
fileRange2 = np.arange(0, len(b)) 
df.to_excel('df.xlsx', header=True, index=False) ###############################
df['stockreturn']=pd.to_numeric(df['stockreturn'])

for i in fileRange2:
    SmallCapReturn = df['stockreturn'].loc[(df["SMB"] == "SCap") & (dfNew['Date1'] == b[i])].mean()
    #df['SCR'].loc[df['Date1'] == a[i]] = SmallCapReturn
    LargeCapReturn = df['stockreturn'].loc[(df["SMB"] == "LCap") & (dfNew['Date1'] == b[i])].mean()
    #df['LCR'].loc[df['Date1'] == a[i]] = LargeCapReturn
    SMB = SmallCapReturn - LargeCapReturn
    df['SMB_f'].loc[(df['Date1'] == b[i])] = SMB
    

FFC =df
FFC.head(10)
FFC.MktPrem.mean()
FFC.SMB_f.mean()
FFC['MktPrem'].astype(float)
FFC['SMB_f']=pd.to_numeric(FFC['SMB_f'])
FFC['MktPrem']=pd.to_numeric(FFC['MktPrem'])
FFC['stockreturn']=pd.to_numeric(FFC['stockreturn'])
FFC2 = FFC.groupby(['Date1'], as_index=False).agg({'MktPrem':np.mean, 'SMB_f':np.mean, 'stockreturn':np.mean})

Y = FFC2.stockreturn.values 
X = FFC2[["MktPrem","SMB_f"]]
X = sm.add_constant(X)
X.rename(columns = {"const":"Intercept"}, inplace = True)

model = sm.OLS( Y.astype(float), X.astype(float) )

result = model.fit()
print (result.params)
print(result.summary())
