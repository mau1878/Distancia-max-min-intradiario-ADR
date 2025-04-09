import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# Define the list of tickers (without .BA suffix initially)
tickers = ["GGAL", "YPFD", "PAMP", "TXAR", "ALUA", "CRES", "SUPV", "CEPU", "BMA", "TGSU2",
           "TRAN", "EDN", "LOMA", "MIRG", "DGCU2", "BBAR", "MOLI", "TGNO4", "CGPA2", "COME",
           "IRSA", "BYMA", "TECO2", "METR", "CECO2", "BHIP", "AGRO", "LEDE", "CVH", "HAVA",
           "AUSO", "VALO", "SEMI", "INVJ", "CTIO", "MORI", "HARG", "GCLA", "SAMI", "BOLT",
           "MOLA", "CAPX", "OEST", "LONG", "GCDI", "GBAN", "CELU", "FERR", "CADO", "GAMI",
           "PATA", "CARC", "BPAT", "RICH", "INTR", "GARO", "FIPL", "GRIM", "DYCA", "POLL",
           "DOME", "ROSE", "MTR", "ECOG"]

# Add .BA suffix to all tickers for Argentine stocks
tickers_with_suffix = [ticker + ".BA" for ticker in tickers]

# Streamlit app title
st.title("Percentage Difference between High and Low for Each Ticker")

# Date range (last 24 hours)
end_date = datetime.now()
start_date = end_date - timedelta(days=1)

# Download data from yfinance
@st.cache_data
def fetch_yfinance_data():
    data = yf.download(tickers_with_suffix, start=start_date, end=end_date, interval="1d")
    return data

try:
    # Fetch data
    stock_data = fetch_yfinance_data()

    # Create an empty DataFrame to store processed data
    processed_data = pd.DataFrame(columns=['symbol', 'high', 'low'])

    # Process the multi-index DataFrame
    for ticker in tickers_with_suffix:
        if ('High', ticker) in stock_data.columns and ('Low', ticker) in stock_data.columns:
            high = stock_data[('High', ticker)].max()
            low = stock_data[('Low', ticker)].min()
            
            # Only include if we have valid data
            if pd.notna(high) and pd.notna(low):
                # Remove .BA suffix for display
                ticker_clean = ticker.replace(".BA", "")
                processed_data = pd.concat([processed_data, 
                                         pd.DataFrame({'symbol': [ticker_clean], 
                                                     'high': [high], 
                                                     'low': [low]})],
                                        ignore_index=True)

    # Calculate percentage difference
    processed_data['perc_diff'] = ((processed_data['high'] - processed_data['low']) / 
                                 processed_data['low']) * 100

    # Sort by percentage difference
    ticker_diff = processed_data[['symbol', 'perc_diff']].sort_values(by='perc_diff', 
                                                                    ascending=False)

    # Plot with Plotly
    fig = px.bar(
        ticker_diff,
        x='perc_diff',
        y='symbol',
        orientation='h',
        title="Percentage Difference between High and Low (Sorted)",
        labels={'perc_diff': 'Percentage Difference (%)', 'symbol': 'Ticker'},
        template="plotly_white",
        text='perc_diff',
        color='perc_diff',
        color_continuous_scale='Viridis'
    )

    # Customize layout
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=25 * len(ticker_diff)
    )

    # Customize text annotations
    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%')

    # Display the plot
    st.plotly_chart(fig)

    # Button to download the image
    if st.button("Download High-Quality Image"):
        fig.write_image("percentage_difference_plot.png", width=1500, height=800, scale=2)
        st.download_button(
            label="Download Image",
            data=open("percentage_difference_plot.png", "rb").read(),
            file_name="percentage_difference_plot.png",
            mime="image/png"
        )

    # Display missing tickers
    fetched_tickers = set(processed_data['symbol'])
    missing_tickers = set(tickers) - fetched_tickers
    if missing_tickers:
        st.write(f"No data found for the following tickers: {', '.join(missing_tickers)}")
    else:
        st.write("Data fetched successfully for all tickers.")

except Exception as e:
    st.error(f"Error fetching data from yfinance: {str(e)}")
