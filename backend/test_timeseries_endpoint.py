"""
Test the new timeseries endpoint directly against Railway database
"""
import os
import requests

# Railway database URL
RAILWAY_API = "https://naija-conflict-tracker-production.up.railway.app"

def test_monthly_trends():
    """Test the monthly trends endpoint"""
    
    print("Testing Monthly Trends Endpoint...")
    print("=" * 50)
    
    # Test 1: All states, last 24 months
    print("\n1. All states (last 24 months with forecast):")
    response = requests.get(f"{RAILWAY_API}/api/v1/timeseries/monthly-trends")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Time Range: {data['timeRange']['start']} to {data['timeRange']['end']}")
        print(f"   Total Months: {data['timeRange']['totalMonths']}")
        print(f"   Avg Incidents/Month: {data['summary']['avgIncidentsPerMonth']}")
        print(f"   Avg Fatalities/Month: {data['summary']['avgFatalitiesPerMonth']}")
        print(f"   Peak Month: {data['summary']['peakMonth']} ({data['summary']['peakIncidents']} incidents)")
        print(f"   Anomaly Count: {data['summary']['anomalyCount']}")
        print(f"   Trend Direction: {data['summary']['trendDirection']}")
        
        if 'forecast' in data:
            print(f"\n   📈 Forecast (next 3 months):")
            for f in data['forecast']['data']:
                print(f"      {f['month']}: {f['predictedIncidents']} incidents (confidence: {f['confidence']})")
        
        # Show last 3 months of actual data
        print(f"\n   Last 3 months of data:")
        for month_data in data['data'][-3:]:
            anomaly = "⚠️ SPIKE" if month_data['isAnomalousIncidents'] else ""
            print(f"      {month_data['month']}: {month_data['incidents']} incidents, {month_data['fatalities']} deaths {anomaly}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
    
    # Test 2: Specific state (Borno)
    print("\n\n2. Borno state (last 12 months):")
    response = requests.get(
        f"{RAILWAY_API}/api/v1/timeseries/monthly-trends",
        params={"state": "Borno", "months_back": 12}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   State: {data['state']}")
        print(f"   Avg Incidents/Month: {data['summary']['avgIncidentsPerMonth']}")
        print(f"   Total Incidents: {data['summary']['totalIncidents']}")
        print(f"   Total Fatalities: {data['summary']['totalFatalities']}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 3: Seasonal Analysis
    print("\n\n3. Seasonal Analysis (All States):")
    response = requests.get(f"{RAILWAY_API}/api/v1/timeseries/seasonal-analysis")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   High Risk Months: {', '.join(data['analysis']['highRiskMonths'])}")
        print(f"   Peak Month: {data['analysis']['peakMonth']}")
        print(f"   Lowest Month: {data['analysis']['lowestMonth']}")
        print(f"\n   Monthly breakdown (top 3):")
        sorted_months = sorted(data['seasonalPattern'], key=lambda x: x['totalIncidents'], reverse=True)
        for month in sorted_months[:3]:
            print(f"      {month['month']}: {month['totalIncidents']} incidents ({month['riskLevel']} risk)")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Test 4: State Comparison
    print("\n\n4. State Comparison (Borno vs Zamfara vs Kaduna):")
    response = requests.get(
        f"{RAILWAY_API}/api/v1/timeseries/trend-comparison",
        params={"states": "Borno,Zamfara,Kaduna", "months_back": 12}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Time Range: {data['timeRange']}")
        for state, state_data in data['comparison'].items():
            print(f"\n   {state}:")
            print(f"      Total Incidents: {state_data['total']}")
            print(f"      Avg/Month: {state_data['avgPerMonth']}")
            print(f"      Data Points: {len(state_data['months'])} months")
    else:
        print(f"❌ Error: {response.status_code}")


if __name__ == "__main__":
    test_monthly_trends()
