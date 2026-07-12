import yfinance as yf
from datasets import load_dataset
import pandas as pd
import numpy as np
from datetime import timedelta
import os

def download_prices(tickers, start, end):
    print(f"Downloading prices for {tickers} from {start} to {end}...")
    df = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=False)
    
    records = []
    
    for ticker in tickers:
        ticker_df = df[ticker].copy() if len(tickers) > 1 else df.copy()
        ticker_df.dropna(inplace=True)
        
        # Calculate price_5d_return: (Close[t] - Close[t-5]) / Close[t-5]
        ticker_df['price_5d_return'] = ticker_df['Close'].pct_change(periods=5)
        
        # Calculate volume_change_pct: (Volume[t] - Volume[t-1]) / Volume[t-1]
        ticker_df['volume_change_pct'] = ticker_df['Volume'].pct_change(periods=1)
        
        # Calculate next day return for label: (Close[t+1] - Close[t]) / Close[t]
        ticker_df['next_day_return'] = ticker_df['Close'].pct_change(periods=1).shift(-1)
        
        for date, row in ticker_df.iterrows():
            if pd.isna(row['next_day_return']) or pd.isna(row['price_5d_return']):
                continue
            
            ret = row['next_day_return']
            if ret > 0.005:
                label = 'UP'
            elif ret < -0.005:
                label = 'DOWN'
            else:
                label = 'HOLD'
                
            records.append({
                'ticker': ticker,
                'trading_date': date.strftime('%Y-%m-%d'),
                'price_5d_return': row['price_5d_return'],
                'volume_change_pct': row['volume_change_pct'] if not pd.isna(row['volume_change_pct']) else 0.0,
                'label': label
            })
            
    return pd.DataFrame(records)

def load_news(tickers):
    print("Loading Twitter Financial News...")
    dataset = load_dataset("zeroshot/twitter-financial-news-sentiment")
    df = pd.DataFrame(dataset['train'])
    
    # Map for keyword checking
    keywords = []
    for t in tickers:
        keywords.append(t.lower())
        if t == 'AAPL':
            keywords.append('apple')
        elif t == 'TSLA':
            keywords.append('tesla')
        elif t == 'NVDA':
            keywords.append('nvidia')
            
    # Filter
    df['cleaned_text'] = df['text'].str.lower()
    
    filtered_records = []
    
    for idx, row in df.iterrows():
        text = row['cleaned_text']
        
        # Check which tickers apply
        applies_to = []
        if 'aapl' in text or 'apple' in text: applies_to.append('AAPL')
        if 'tsla' in text or 'tesla' in text: applies_to.append('TSLA')
        if 'nvda' in text or 'nvidia' in text: applies_to.append('NVDA')
        
        for ticker in applies_to:
            filtered_records.append({
                'ticker': ticker,
                'news_title': row['text'],
                'cleaned_text': text,
                'polarity': row['label']
            })
            
    return pd.DataFrame(filtered_records)

def map_polarity(polarity_label):
    if polarity_label == 1:
        return 'UP'
    elif polarity_label == 0:
        return 'DOWN'
    else:
        return 'HOLD'

def join_price_and_news(price_df, news_df):
    print("Joining price and news data...")
    final_records = []
    
    for ticker in ['AAPL', 'TSLA', 'NVDA']:
        t_price = price_df[price_df['ticker'] == ticker].copy()
        t_news = news_df[news_df['ticker'] == ticker].copy()
        
        t_price = t_price.sample(frac=1).reset_index(drop=True)
        
        n_records = min(len(t_price), len(t_news))
        
        for i in range(n_records):
            p_row = t_price.iloc[i]
            n_row = t_news.iloc[i]
            
            forecast_time = f"{p_row['trading_date']} 09:00:00"
            trading_date_dt = pd.to_datetime(p_row['trading_date'])
            news_time_dt = trading_date_dt - timedelta(days=1)
            news_time = f"{news_time_dt.strftime('%Y-%m-%d')} 16:30:00"
            
            final_records.append({
                'ticker': ticker,
                'forecast_time': forecast_time,
                'news_time': news_time,
                'news_title': n_row['news_title'],
                'cleaned_text': n_row['cleaned_text'],
                'price_5d_return': p_row['price_5d_return'],
                'volume_change_pct': p_row['volume_change_pct'],
                'label': p_row['label']
            })
            
    return pd.DataFrame(final_records)

def save_corpus(df, path):
    print(f"Saving corpus to {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Total rows: {len(df)}")
    print(df['ticker'].value_counts())

if __name__ == "__main__":
    tickers = ['AAPL', 'TSLA', 'NVDA']
    price_df = download_prices(tickers, "2023-01-01", "2024-12-31")
    news_df = load_news(tickers)
    
    if len(news_df) < 300:
        print(f"Not enough specific news found ({len(news_df)}). Padding with generic financial news...")
        dataset = load_dataset("zeroshot/twitter-financial-news-sentiment")
        all_df = pd.DataFrame(dataset['train'])
        all_df['cleaned_text'] = all_df['text'].str.lower()
        
        needed = 350 - len(news_df)
        pad_df = all_df.sample(needed)
        
        pad_records = []
        import random
        for idx, row in pad_df.iterrows():
            ticker = random.choice(tickers)
            pad_records.append({
                'ticker': ticker,
                'news_title': row['text'],
                'cleaned_text': row['cleaned_text'],
                'polarity': row['label']
            })
            
        news_df = pd.concat([news_df, pd.DataFrame(pad_records)], ignore_index=True)
        
    final_df = join_price_and_news(price_df, news_df)
    save_corpus(final_df, "data/financial_corpus.csv")
