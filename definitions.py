import finviz
import numpy as np
import urllib.parse
import json
import requests
import pandas as pd
import time

#
# This file contails all the definitions that are used in the fcf/roic model.
#
# @author Sjoerd van der Heijden
#

# When this definition is called, a dictionaty is converted into a string

def Dict_to_string(dictionary): 
    
    array=list(dict.values(dictionary))
    
    array = np.asarray(array)
    
    array=array.astype(float)
    
    return(array)

#when this definition is called, the cash flow statement of a company is requested and stored

def fmp_cfs(ticker):
    
    time.sleep(1)
    
    url_fmp = 'https://financialmodelingprep.com/api/v2/financials/cash-flow-statement/'
    
    url_ticker = urllib.parse.urljoin(url_fmp, ticker)
    
    response_cfs = requests.get(url_ticker)
    
    cfs_data = json.loads(response_cfs.text.replace("<pre>","").replace("</pre>",""))
    
    return(cfs_data)
    
#when this definition is called, the income statement of a company is requested and stored

def inc_cfs(ticker):
    
    time.sleep(1)
    
    url_fmp = 'https://financialmodelingprep.com/api/v2/financials/income-statement/'
    
    url_ticker = urllib.parse.urljoin(url_fmp, ticker)
    
    response_is = requests.get(url_ticker)
    
    is_data = json.loads(response_is.text.replace("<pre>","").replace("</pre>",""))
    
    return(is_data)
    
#when this definition is called, the balance sheet of a company is requested and stored
    

def fmp_bs(ticker):
    time.sleep(1)
    url_bs = 'https://financialmodelingprep.com/api/v2/financials/balance-sheet-statement/'
    url_ticker = urllib.parse.urljoin(url_bs, ticker)
    response_bs = requests.get(url_ticker)
    bs_data = json.loads(response_bs.text.replace("<pre>","").replace("</pre>",""))
    return(bs_data)
    
#when this definition is called, the oweners earnings of a company is computed

    
def owners_earnings(ticker):
    
    cfs_data = fmp_cfs(ticker)
    
    is_data = inc_cfs(ticker)
    
    try:
        
        fcf = float(cfs_data['financials'][4]['Free cash flow'])
        
        inc = float(is_data['financials'][4]['Net income'])
        
        if (inc <= 1.3*fcf):
            
            fcf = inc
            
        else:
            
            fcf = 0
            
    except:
        
        fcf = float(is_data['financials'][4]['Net income'])
        
    return(fcf)
    
# when this definition is called, information from finviz and financial moddeling pred is requested if available. If not,
# assumptions are made. 
    
def fnvz(ticker):
    
    try:
        
        g = float(finviz.get_stock(ticker)['EPS next 5Y'].rstrip("%"))/100
        
    except:
        
        try:
            
            g = float(finviz.get_stock(ticker)['EPS past 5Y'].rstrip("%"))/100
            
        except:
            
            g = 0.05
            
    try:
        
        price = float(finviz.get_stock(ticker)['Price'])
        
        mc = float(float(str(finviz.get_stock(ticker)['Market Cap']).replace('B', ''))*1e9)
        
    except:
        
        url_prof = 'https://financialmodelingprep.com/api/company/profile/'
        
        url_ticker = urllib.parse.urljoin(url_prof, ticker)
        
        response_prof = requests.get(url_ticker)
        
        prof_data = json.loads(response_prof.text.replace("<pre>","").replace("</pre>",""))
        
        price = float(prof_data[ticker]['Price'])
        
        mc = float(prof_data[ticker]['MktCap'])
        
    try:
        
        EPS = float(finviz.get_stock(ticker)['EPS next Y'])
        
    except:
        
        EPS = 0
        
    return(g,
           price,
           mc,
           EPS)
    
# When this method is called, a basic fcf model is computed.
    
def pv(fcf,mc,price,g,d,EPS):
    
    pv = np.zeros(5)
    
    nr_sh = (mc/price)/1000000
    
    if fcf >= 0:
        
        for i in range(0,5):
            
            dcount = (1/(1+d))**(i+1)
            
            gwth = (1+g)**(i+1)
            
            pv[i] = fcf*gwth*dcount
            
        pv_sum = np.sum(pv)
        
        perp = (pv[4]/d)
        
        pv_tot = pv_sum+perp
        
        pv_stock = pv_tot/nr_sh
        
        mos = pv_stock/price
        
    else:
        
        mos = 0
        
    return(mos)

#when this method is called scoring is done.

def scoring(mos_results, roic_result):
    
    mos_rank = []
    
    score = []
    
    sort_key = sorted(mos_results.items(), 
                         key = lambda t: t[1], reverse=True)
    
    ziplist = list(zip(*sort_key))
    
    mos_rank = list(ziplist[0])
    
    roic_rank = []
    
    sort_key = sorted(roic_result.items(), 
                         key = lambda t: t[1], reverse=True)
    
    ziplist = list(zip(*sort_key))
    
    roic_rank = list(ziplist[0])
    
    for i in mos_results:
        
        score = np.append(score, mos_rank.index(i)+roic_rank.index(i))
        
    return(score)
    
# when this method is called, info for presentation is obtained.     
    
def info_fmp(score,mos_results,total_results_dict,current_result,roic_result,growth_result):
    
    tickers = []
    
    roic = []
    
    industry=[]
    
    mos = []
    
    companyname=[]
    
    sector=[]
    
    lastprice=[]
    
    current = []
    
    beta = []
    
    date = []
    
    growth = []
    
    for i in mos_results:
        
        Profile = 'https://financialmodelingprep.com/api/company/profile/'
        
        url_profile = urllib.parse.urljoin(Profile, i)
        
        response_profile = requests.get(url_profile)
        
        Profile = json.loads(response_profile.text.replace("<pre>","").replace("</pre>",""))
        
        industry.append(Profile[i]["industry"])
        
        companyname.append(Profile[i]["companyName"])
        
        sector.append(Profile[i]["sector"])
        
        lastprice.append(Profile[i]["Price"])
        
        tickers.append(i)
        
        mos.append(mos_results[i]*100)
        
        growth.append(growth_result[i])
        
        current.append(current_result[i])
        
        roic.append(roic_result[i])
        
        is_data = inc_cfs(i)
        
        date.append(is_data['financials'][4]['date'])
        
        try:
            
            beta.append(Profile[i]["Beta"])
            
        except:
            
            B = 0
            
            beta.append(B)
            
    final_result = np.transpose(np.array([score,
                                          tickers,
                                          companyname, 
                                          sector, 
                                          industry,
                                          lastprice,
                                          current,
                                          mos,
                                          roic,
                                          growth,
                                          beta,
                                          date]))
    
    return(final_result)
    
# when this definition is called, a dataframe is constructed. Some sectors are removed from the set.
    
def dataframe(final_result):
    
    final_result = pd.DataFrame(final_result, columns=['Score',
                                                       'Ticker',
                                                       'Company Name',
                                                       'Sector',
                                                       'Industry',
                                                       'Last Price',
                                                       'Current Ratio', 
                                                       '% MoS', 
                                                       '% ROIC',
                                                       '% 5Y G. Rate',
                                                       'Beta',
                                                       'Most Recent Data']).sort_values(by=['Score'],ascending=True, kind='mergesort')
    
    final_result = final_result[final_result.Industry != 'Biotechnology']
    
    final_result = final_result[final_result.Industry != 'Drug Manufacturers']
    
    final_result = final_result[final_result.Sector != 'Financial Services']
    
    final_result = final_result[final_result.Sector != 'Real Estate']
    
    return(final_result)
    
# when this definition is called, the invested capital is computed.    
    
def invested_capital(ticker):
    
    bs_data = fmp_bs(ticker)
    
    try:
        
        current_assets = float(bs_data['financials'][4]['Total current assets'])
        
        current_liab = float(bs_data['financials'][4]['Total current liabilities'])
        
        working_cap = current_assets-current_liab
        
        current_ratio = current_assets/current_liab
        
        if (working_cap <= 0):
            
            working_cap = 0
            
    except:
        
        working_cap = 0
        
        current_ratio = 0
        
    try:
        
        ppe = float(bs_data['financials'][4]["Net property, plant and equipment"])
        
    except:
        
        try:
            
            ppe = float(bs_data['financials'][4]["Property and equipment"])
            
        except:
            
            try:
                
                ppe = float(bs_data['financials'][4]["Real estate properties, net"]) 
                
            except:
                
                try:
                    
                    ppe = float(bs_data['financials'][4]["Premises and equipment"]) 
                    
                except:
                    
                    equity = float(bs_data['financials'][4]["Total stockholders' equity"]) 
                    
    try:
        
        invested_capital = working_cap + ppe
        
    except:
        
        invested_capital = equity
        
    return(invested_capital,current_ratio)



    
    
