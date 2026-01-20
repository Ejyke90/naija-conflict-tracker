from prophet import Prophet
import pandas as pd
from app.db.database import engine  # Assume database connection

def load_data():
    query = 'SELECT * FROM conflict_articles'  # Adjust based on schema
    df = pd.read_sql_query(query, engine)
    df['ds'] = pd.to_datetime(df['date_column'])  # Ensure date column is present
    df = df.rename(columns={'incident_count': 'y'})  # Example target variable
    return df

def train_forecast_model():
    df = load_data()
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=30)  # Forecast next 30 days
    forecast = model.predict(future)
    return forecast

if __name__ == '__main__':
    forecast = train_forecast_model()
    print(forecast)
