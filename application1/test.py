from fastapi import FastAPI, Header, HTTPException
from typing import List, Optional
import requests

app = FastAPI()

window_size = 10
numbers_window = []

def calculate_average(numbers: List[int]) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def fetch_numbers_from_server(numberid: str, headers: dict) -> List[int]:
    url = f"http://20.244.56.144/test/{numberid}"
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        numbers = data.get("numbers", [])
        return numbers
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching numbers: {str(e)}")

@app.post("/numbers/{numberid}")
async def get_numbers(numberid: str, token_type: Optional[str] = Header(None), access_token: Optional[str] = Header(None)):
    if token_type != "Bearer":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        headers = {
            "Authorization": f"{token_type} {access_token}",
            "Content-Type": "application/json"
        }
        numbers_from_server = fetch_numbers_from_server(numberid, headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching numbers: {str(e)}")
    
    new_numbers = [num for num in numbers_from_server if num not in numbers_window]
    numbers_window.extend(new_numbers)

    if len(numbers_window) > window_size:
        numbers_window[:] = numbers_window[-window_size:]

    current_average = calculate_average(numbers_window)

    response = {
        "numbers_from_server": numbers_from_server,
        "previous_window_state": {
            "numbers": numbers_window[:-len(new_numbers)],
            "average": calculate_average(numbers_window[:-len(new_numbers)])
        },
        "current_window_state": {
            "numbers": numbers_window,
            "average": current_average
        }
    }

    return response
