import streamlit as st
import numpy as np
import pandas as pd,plotly_express as px,yfinance as yf
st.title("Stock Dashboard")
data = None
try:
    ticker = st.sidebar.text_input('Ticker')

    start_d = st.sidebar.date_input('Start date')
    end_d = st.sidebar.date_input('End date')

    if start_d >= end_d:
        st.error("Error: The start date must be earlier than the end date.")
    else:
        if ticker:
            data = yf.download(ticker, start=start_d, end=end_d)
        else:
            st.error("Error: Please enter a valid ticker symbol.")
        
    
    if data is not None and data.empty:
        st.error("Error: No data found for the selected ticker and date range. Please try again.")
    else:
        fig = px.line(data, x=data.index, y='Adj Close', title=f'{ticker} Stock Prices')
        st.plotly_chart(fig)

except ValueError as ve:
    st.error(f"ValueError occurred: {ve}\n Enter a valid Tinker")
    
except AttributeError as ae:
    st.error(f"The Data loaded is Empty.Please Change the attributes accordingly.")

except Exception as e:
    st.error(f"An error occurred: {e}")
    data = None

finally:
    st.write("Stock Dashboard Loaded")
    
pricing_data,fundamental_data,news = st.tabs(["Pricing Data","Fundamental Data","News"])
    
if data is not None and ticker:
    with pricing_data:
        st.header("PRICING DATA")
        data2=data.copy()
        data2['% change'] = data['Adj Close']/ data['Adj Close'].shift(1) -1
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return =data2['% change'].mean()*252*100
        st.write("the annual return is :",annual_return,"%")
        stdev=np.std(data2['% change'])*np.sqrt(252)
        st.write("The Standard Deviation :",stdev*100,"%")
        if stdev > 0:
            risk_adjusted_return = annual_return / (stdev * 100)
            st.write(f"Risk Adjusted Return (Sharpe Ratio): {risk_adjusted_return:.2f}")
        else:
            st.write("Standard Deviation is 0, cannot calculate Risk Adjusted Return.")
        
    with fundamental_data:
        stock = yf.Ticker(ticker)
        balance_sheet = stock.balance_sheet
        income_statement = stock.financials
        cash_flow = stock.cashflow    
        df_balance_sheet = pd.DataFrame(balance_sheet)
        df_income_statement = pd.DataFrame(income_statement)
        df_cash_flow = pd.DataFrame(cash_flow)
        st.subheader("Balance Header")
        st.write(df_balance_sheet)
        st.subheader("Income Statement")
        st.write(df_income_statement)
        st.subheader("Cash Flow Statement")
        st.write(df_cash_flow)
        
    import finnhub
    from datetime import datetime
    with news:
        st.header(f"News of {ticker}")
        finnhub_client = finnhub.Client(api_key='crd00phr01qkg0hdrb60crd00phr01qkg0hdrb6g')
        news = finnhub_client.company_news(ticker, _from=start_d, to=end_d)
        recent_news = news[:10]
        news_data = []
        for article in recent_news:
            news_data.append({
                'Published': datetime.utcfromtimestamp(article['datetime']).strftime('%Y-%m-%d %H:%M:%S'),
                'Title': article['headline'],
                'Summary': article['summary'],
                'URL': article['url']
            })
        df_news = pd.DataFrame(news_data)
        for i in range(10):
            st.subheader(f'News {i+1}')
            st.write(df_news['Published'][i])
            st.write(df_news['Title'][i])
            st.write(df_news['Summary'][i])
            st.write(df_news['URL'][i])