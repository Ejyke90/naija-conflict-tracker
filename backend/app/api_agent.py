from fastapi import APIRouter, Depends
from app.agent_orchestrator import route_agent
from app.db.database import engine  # Assume database connection
import pandas as pd

router = APIRouter()

@router.get('/agents/route')
def route_agent_endpoint(query: str):
    agent = route_agent(query)  # Use orchestrator routing
    return {'agent_routed': agent}

@router.get('/data/conflicts')
def get_conflicts():
    df = pd.read_sql_query('SELECT * FROM conflict_articles', engine)  # Example query
    return df.to_dict(orient='records')

# Add more endpoints as needed for other agents
