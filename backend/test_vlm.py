import os, json, httpx, base64, requests
os.environ['MINIMAX_API_KEY'] = 'sk-cp-GspJ9IWg8GDbzzFWFH_V4I9FQ_w1QUrAyFaoiXZFX99gZb55TOoXw3ZxdcnSv5hfIFWpbDaDgKTV_4vcm28I1qsA7LIJj28zkKS4QEnDTaIh1LFpfKkPRFw'
os.environ['MINIMAX_API_HOST'] = 'https://api.minimax.io'
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('MINIMAX_API_KEY', '')
host = os.environ.get('MINIMAX_API_HOST', '')

# Check coding plan usage first
url = f'{host}/v1/api/openplatform/coding_plan/remains'
headers = {'Authorization': f'Bearer {api_key}', 'MM-API-Source': 'Minimax-MCP'}
r = requests.get(url, headers=headers, timeout=15)
print('Usage check status:', r.status_code)
print('Usage check response:', r.text[:500])
