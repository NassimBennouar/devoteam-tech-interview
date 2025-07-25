import requests
import streamlit as st
import json
import os

class APIClient:
    def __init__(self):
        # Use environment variable or default to localhost:8000 for local dev
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api")
    
    def get_history(self, limit=100, start_time=None, end_time=None):
        """Get historical metrics data from FastAPI"""
        try:
            params = {"limit": limit}
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            response = requests.get(f"{self.base_url}/history", params=params)
            
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
    
    def get_metrics_info(self):
        """Get metrics info (count and latest timestamp) from FastAPI"""
        try:
            response = requests.get(f"{self.base_url}/metrics/info")
            
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

    def get_historical_analysis(self, points=50):
        """Get historical LLM analysis from FastAPI"""
        try:
            response = requests.get(f"{self.base_url}/analysis/historical", params={"points": points})
            
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