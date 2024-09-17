import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Lista de tickers
tickers = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS', 'LOMA', 'PAM', 'SUPV', 'TEO', 'TGS', 'YPF']

st.title("Análisis de Distancia Porcentual Máx-Mín entre Fechas")

# Seleccionar el rango de fechas
start_date, end_date = st.date_input(
    "Seleccione el rango de fechas",
    [datetime.now().date() - timedelta(days=30), datetime.now().date()]
)

# Verificar que las fechas sean válidas
if start_date > end_date:
    st.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
else:
    @st.cache_data
    def fetch_data(ticker, start_date, end_date):
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date)
            if stock_data.empty:
                st.warning(f"No se encontraron datos para {ticker}.")
                return pd.DataFrame()
            stock_data['Date'] = stock_data.index.date  # Ensure date is a column
            stock_data = stock_data.reset_index(drop=True)  # Avoid ambiguity
            return stock_data
        except Exception as e:
            st.error(f"Error al obtener datos para {ticker}: {e}")
            return pd.DataFrame()

    def calculate_distance_for_day(day_data):
        max_price = day_data['High']
        min_price = day_data['Low']
        if min_price == 0:
            return None
        # Calcular la distancia porcentual
        percentage_distance = ((max_price - min_price) / min_price) * 100
        return percentage_distance

    def get_distance_data(ticker, start_date, end_date):
        data = fetch_data(ticker, start_date, end_date)
        if data.empty:
            return None
        # Añadir las columnas de precios de cierre, máximo y mínimo
        data['Distance (%)'] = data.apply(calculate_distance_for_day, axis=1)
        return data[['Date', 'Close', 'High', 'Low', 'Distance (%)']].dropna()  # Drop rows with NaN values

    # Obtener la distancia máx-mín para todas las fechas entre el rango
    all_data = []
    for ticker in tickers:
        try:
            ticker_data = get_distance_data(ticker, start_date, end_date)
            if ticker_data is not None:
                ticker_data['Ticker'] = ticker
                all_data.append(ticker_data)
        except Exception as e:
            st.error(f"Error al procesar datos para {ticker}: {e}")

    if all_data:
        # Concatenar los datos de todos los tickers
        combined_df = pd.concat(all_data)

        # Verificar que la columna 'Date' exista
        if 'Date' not in combined_df.columns:
            st.error("La columna 'Date' no se encontró en los datos.")
        else:
            # Calcular la mediana de la distancia por cada fecha
            combined_df['Date'] = pd.to_datetime(combined_df['Date'])  # Ensure 'Date' is in datetime format
            median_distances = combined_df.groupby('Date')['Distance (%)'].median().reset_index()  # Reset index here
            median_distances = median_distances.rename(columns={'Distance (%)': 'Median Max-Min Distance (%)'})
            
            # Ordenar por la distancia mediana en orden descendente
            top_10_days = median_distances.sort_values(by='Median Max-Min Distance (%)', ascending=False).head(10)
            
            # Mostrar las 10 fechas con mayor distancia mediana
            st.subheader(f"Top 10 días con mayor distancia porcentual mediana máx-mín entre {start_date} y {end_date}")
            st.dataframe(top_10_days)

            # Crear tablas individuales para cada fecha
            st.subheader("Tablas para cada uno de los Top 10 días")
            for idx, row in top_10_days.iterrows():
                day = row['Date'].date()  # Convert to date format for matching
                st.write(f"### Día: {day}")
                
                # Filtrar los datos para ese día y mostrar los 10 tickers con mayor distancia porcentual
                day_data = combined_df[combined_df['Date'] == day]
                
                if day_data.empty:
                    st.warning(f"No data available for {day}.")
                else:
                    # Mostrar los tickers junto con el precio de cierre, máximo, mínimo y la distancia porcentual
                    day_data = day_data.sort_values(by='Distance (%)', ascending=False).head(10)
                    st.dataframe(day_data[['Ticker', 'Close', 'High', 'Low', 'Distance (%)']])
    else:
        st.write("No hay datos válidos disponibles para graficar.")
