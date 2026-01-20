import re
from fastapi import Request
from app.api.v1.api import api_router as api_v1_router

AGENT_ROUTING = {
    'data_science': 'DATA_SCIENCE_AGENT',
    'geospatial': 'GEOSPATIAL_AGENT',
    'scraping': 'SCRAPING_AGENT',
    'etl': 'ETL_AGENT',
    'dataviz': 'DATAVIZ_AGENT',
    'cartography': 'CARTOGRAPHY_AGENT',
    'geospatial_agent': 'GEOSPATIAL_AGENT',  # Add geospatial agent routing
    'api': 'API_AGENT'
    # Add more agents as needed based on AGENTS.md
}

def route_agent(request: Request):
    text = request.query_params.get('query', '')
    for key in AGENT_ROUTING:
        if re.search(key, text, re.IGNORECASE):
            return AGENT_ROUTING[key]
    return 'DEFAULT_AGENT'  # Fallback if no match

# Example endpoint for routing (integrate with main API)
@api_v1_router.get('/route_agent')
def agent_route(query: str):
    agent = route_agent(Request(scope={'query_params': query}))  # Simulate request for simplicity
    return {'routed_agent': agent}
