import pandas as pd
from sqlalchemy import create_engine
from app.db.database import engine  # Assume database connection from scaffolding

def load_data_to_db(data, table_name):
    df = pd.DataFrame(data)
    df.to_sql(table_name, engine, if_exists='append', index=False)

# Example ETL for scraped data
def etl_pipeline(scraped_data):
    # Transform: Basic cleaning, e.g., remove duplicates
    cleaned_data = [dict(t) for t in {tuple(d.items()) for d in scraped_data}]
    # Load into database
    load_data_to_db(cleaned_data, 'conflict_articles')

if __name__ == '__main__':
    # Simulate input from scraping_agent
    sample_data = [{'title': 'Sample Title', 'content': 'Sample Content'}]
    etl_pipeline(sample_data)
