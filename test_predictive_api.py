"""
Quick test of Predictive Analytics API
"""
import requests
import json

def test_api(url, name):
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
        else:
            print(f"✅ Success!")
            if 'forecast_period' in data:
                print(f"   Forecast Period: {data['forecast_period']}")
            if 'historical_summary' in data:
                print(f"   Historical Summary:")
                for key, value in data['historical_summary'].items():
                    print(f"     - {key}: {value}")
            if 'forecasts' in data:
                print(f"   Number of Forecasts: {len(data['forecasts'])}")
                if data['forecasts']:
                    print(f"   First Forecast:")
                    print(json.dumps(data['forecasts'][0], indent=6))
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:8000"
    
    # Test Revenue Forecast
    test_api(
        f"{base_url}/reports/predictive/revenue-forecast?months_ahead=6&include_confidence=true",
        "Revenue Forecast"
    )
    
    # Test Expense Forecast
    test_api(
        f"{base_url}/reports/predictive/expense-forecast?months_ahead=6&include_confidence=true",
        "Expense Forecast"
    )
    
    # Test Cash Flow Forecast
    test_api(
        f"{base_url}/reports/predictive/cash-flow-forecast?months_ahead=6",
        "Cash Flow Forecast"
    )
    
    print(f"\n{'='*70}")
    print("Tests Complete!")
    print(f"{'='*70}\n")
