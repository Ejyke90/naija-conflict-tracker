import pandas as pd
from app.db.database import engine  # Assume database connection

def prepare_timeseries_data(table_name='conflict_articles'):
    query = f'SELECT date_column, incident_count FROM {table_name}'  # Adjust columns
    df = pd.read_sql_query(query, engine)
    df['date_column'] = pd.to_datetime(df['date_column'])
    df.set_index('date_column', inplace=True)
    return df.resample('D').mean()  # Daily resampling example

def detect_anomalies(df):
    # Simple anomaly detection, e.g., using z-score
    df['rolling_mean'] = df['incident_count'].rolling(window=7).mean()
    df['std'] = df['incident_count'].rolling(window=7).std()
    df['z_score'] = (df['incident_count'] - df['rolling_mean']) / df['std']
    anomalies = df[abs(df['z_score']) > 3]
    return anomalies

if __name__ == '__main__':
    df = prepare_timeseries_data()
    anomalies = detect_anomalies(df)
    print(anomalies)
