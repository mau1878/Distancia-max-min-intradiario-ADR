import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Lista de tickers
tickers = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS', 'LOMA', 'PAM', 'SUPV', 'TEO', 'TGS', 'YPF']

st.title("Distancia entre Precios Máximos y Mínimos en una Fecha")

# Seleccionar la fecha para mostrar los datos
selected_date = st.date_input("Seleccione la fecha", datetime.now().date() - timedelta(days=1))

@st.cache_data
def fetch_data(ticker, selected_date):
    try:
        start_date = (selected_date - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        
        if stock_data.empty:
            st.warning(f"No se encontraron datos para {ticker}.")
            return pd.DataFrame()
        
        return stock_data
    except Exception as e:
        st.error(f"Error al obtener datos para {ticker}: {e}")
        return pd.DataFrame()

def get_price_range(ticker, selected_date):
    data = fetch_data(ticker, selected_date)
    
    if data.empty or selected_date not in data.index.date:
        return None, None, None
    
    # Obtener los precios máximo y mínimo
    day_data = data[data.index.date == selected_date]
    if day_data.empty:
        return None, None, None
    
    max_price = day_data['High'].iloc[0]
    min_price = day_data['Low'].iloc[0]
    
    return max_price, min_price, round(max_price - min_price, 2)

ticker_data = []

for ticker in tickers:
    try:
        max_price, min_price, price_range = get_price_range(ticker, selected_date)
        if max_price is None:
            continue
        
        ticker_data.append({
            'Ticker': ticker,
            'Precio Máximo': round(max_price, 2),
            'Precio Mínimo': round(min_price, 2),
            'Distancia Máx-Mín': price_range
        })
    except Exception as e:
        st.error(f"Error al procesar datos para {ticker}: {e}")

df = pd.DataFrame(ticker_data)

# Mostrar la tabla de precios máximos, mínimos y distancia entre ellos
st.subheader(f"Distancia entre Precios Máximos y Mínimos el {selected_date.strftime('%Y-%m-%d')}")
st.dataframe(df)

if not df.empty:
    # Crear gráfico de barras para la distancia entre precios
    fig = px.bar(df, x='Ticker', y='Distancia Máx-Mín', color='Distancia Máx-Mín',
                 color_continuous_scale='Viridis',
                 title=f"Distancia entre Precios Máximos y Mínimos el {selected_date.strftime('%Y-%m-%d')}",
                 labels={'Distancia Máx-Mín': 'Distancia Máx-Mín (Precio Máximo - Precio Mínimo)'})
    
    # Agregar marca de agua al gráfico
    fig.update_layout(xaxis_title='Ticker', yaxis_title='Distancia Máx-Mín (USD)', yaxis_categoryorder='total ascending')
    fig.update_traces(marker=dict(line=dict(width=1, color='rgba(0,0,0,0.2)')))
    
    fig.add_annotation(
        text="MTaurus - X: MTaurus_ok",
        xref="paper", yref="paper",
        x=0.5, y=-0.1,
        showarrow=False,
        font=dict(size=10, color="rgba(0,0,0,0.5)"),
        align="center"
    )
    
    st.plotly_chart(fig)
else:
    st.write("No hay datos válidos disponibles para graficar.")
