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
    
def search_by_param(data, param):
    for item in data:
        if item[param].lower() == param.lower():
            return item
    return []


if __name__ == "__main__":
    # Example usage
    makeup_data = get_makeup_data()
    foundation = "Foundation"
    res = search_by_param(makeup_data, foundation)
    print(res)
    
