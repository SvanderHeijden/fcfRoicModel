#----------------------------main code bf app----------------------------------
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import requests
import definitions as df
from tqdm import tqdm


#------------------------------main function-----------------------------------

def main():
    #-------------------------defining some dict-------------------------------
    
    mos_results={}
    roic_result={}
    total_results_dict={}
    current_result = {}
    growth_result = {}
    #------------------------defining some lists-------------------------------
    
    error_list = []
    tickers = []
    #------------------------importing  tickers--------------------------------
    
    list_tickers = open("ticker.csv").readlines()
    
    #test list_tickers = ['MSFT', 'AAPL']
    
    #-------------------------setting discount rate----------------------------
    
    d = 0.1
    
    #--------------------------start of main-----------------------------------
    
    for i in tqdm(range(len(list_tickers))):
        
        ticker = str(list_tickers[i]).strip()
        
        try:
            
            fcf = df.owners_earnings(ticker)
            
            invested_capital,current_ratio = df.invested_capital(ticker)
            
            roic = fcf/invested_capital
            
            g, price, mc, EPS = df.fnvz(ticker)
            
            mos = df.pv(fcf,mc,price,g,d, EPS)
            
            mos_results[ticker] = round(mos,2)
            
            roic_result[ticker] = round(roic*100,0)
            
            growth_result[ticker] = round(g*100, 1)
            
            current_result[ticker] = round(current_ratio,1)
            
            total_results_dict[ticker]={"Stock Price":price,
                                  "Ticker": ticker,
                                  "Expected 5 Year Growth Rate" :round(g, 2)*100,
                                  "Margin of Safety":round(mos*100-100,2),
                                  "ROIC": round(roic*100,0),
                                  "Free Cash Flow": fcf,
                                  "Current Ratio": current_ratio
                                  }
        except:
            
            error_list.append(ticker)  
            
    score = df.scoring(mos_results, roic_result)
    
    final_result = df.info_fmp(score,mos_results,tickers,current_result,roic_result,growth_result)
    
    final_result = df.dataframe(final_result)
    
    #final_result = final_result[final_result.Sector == 'Consumer Defensive']
    
    #final_result = final_result[final_result.Sector == 'Communication Services']
    
    return(final_result,error_list,mos_results,total_results_dict,roic_result)
    
if __name__ == '__main__':
    final_result,error_list,mos_results,total_results_dict,roic_result = main()
    
    