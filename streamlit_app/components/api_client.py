import requests
import streamlit as st
import json

class APIClient:
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
    
    def ingest_metrics(self, metrics_data):
        """Send metrics to FastAPI ingestion endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/ingest", 
                json=metrics_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_detail = error_data["detail"]
                    elif "errors" in error_data:
                        error_detail = f"Validation errors: {len(error_data['errors'])} issues"
                except:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                
                return {"success": False, "error": error_detail}
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to API server. Make sure FastAPI is running on localhost:8000"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    def get_anomalies(self):
        """Get anomalies from FastAPI"""
        try:
            response = requests.get(f"{self.base_url}/anomalies")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                
                return {"success": False, "error": error_detail}
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to API server"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    def get_analysis(self):
        """Get LLM analysis from FastAPI"""
        try:
            response = requests.get(f"{self.base_url}/analysis")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", f"HTTP {response.status_code}")
                except:
                    error_detail = f"HTTP {response.status_code}: {response.text}"
                
                return {"success": False, "error": error_detail}
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to API server"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"} 