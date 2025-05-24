import requests
import json

## query parameter should be the name of the product
## searching
def get_makeup_data():
    ## returns the json file of the makeup data
    url = "https://makeup-api.herokuapp.com/api/v1/products.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        makeup_data = response.json()
        return makeup_data
    else:
        print("Error: Could not fetch data.")
        return None
    
def search_by_name(data, name):
    if data:
        for item in data:
            if item['name'].lower() == name.lower():
                return item
    return []

if __name__ == "__main__":
    # Example usage
    makeup_data = get_makeup_data()
    lippie = "Lippie Pencil"
    res = search_by_name(makeup_data, lippie)
    print(res)
    