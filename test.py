import requests
from io import BytesIO
from PIL import Image #classes for displaying the graphs


base_url = "http://127.0.0.1:5000"

# Function to test getting countries by continent or the whole world
def test_get_countries_by_continent(continent=None):
    endpoint = "/countries"
    if continent:
        endpoint = f"/countries/{continent}"
    response = requests.get(base_url + endpoint)
    if continent == None:
        print(f"The countries around the world are",response.json())
        print()
    else:
        print(f"The countries in {continent} are",response.json())
        print()

# Function to test getting country details
def test_get_country_details(country):
    endpoint = f"/country/{country}"
    response = requests.get(base_url + endpoint)
    data = response.json()
    print(f"Details about {data['country']}: ")
    print(f"Capital city: {data['capital'][0]} ")
    print(f"Capital city latitude and longtitude: {data['latitude']}, {data['longtitude']} ")
    print(f"Area: {data['area']} ")
    print(f"Population: {data['population']} ")
    print()

# Function to test getting current temperature of a country
def test_get_current_temperature(country):
    endpoint = f"/weather/current/{country}"
    response = requests.get(base_url + endpoint)
    data = response.json()
    print(f"Current temperature in {data['country']} is {data['current_temp']}°C")
    print(f"Current weather in {data['country']} is {data['current_weather']}")
    print()

def favourite(country):
    endpoint = "/favourites"
    header = {
        'Content-Type': 'application/json',
    }
    response = requests.post(base_url + endpoint + '?country='+country,headers=header)
    print("Favorited:", country)
    print()

def unfavourite(country):
    endpoint = "/favourites"
    response = requests.delete(base_url + endpoint + '?country='+country)
    print("Unfavorited:", country)
    print()

def printFavourites():
    endpoint = "/favourites"
    response = requests.get(base_url+endpoint)
    print("List of favourited countries: ",response.json())
    print()

# Function to test favoriting/unfavoriting a country
def test_favorite_unfavorite(country):
    favourite(country)
    printFavourites()
    unfavourite(country)
    printFavourites()


# Function to test generating a line graph of temperature forecast
def test_generate_temperature_forecast(country, n):
    endpoint = f"/weather/forecast/{country}"
    payload = {"days": n}
    response = requests.get(base_url + endpoint, params=payload)
    print("Temperature Forecast for", country, "for the next", n, "days:")
    print()
    img = Image.open(BytesIO(response.content))
    img.show()

# Function to find and favorite the warmest country in South America
def favorite_warmest_country_in_south_america():
    endpoint = "/weather/hottest"
    payload = {"region": "South America"}
    response = requests.get(base_url + endpoint,params=payload)
    data = response.json()
    warmest_country = data["country"]
    temp = data['temperature']
    print(f"Warmest country in South America is {warmest_country} with {temp} °C")
    print()
    
    # Favorite the warmest country
    favourite(warmest_country)
    printFavourites()
    # Generate temperature forecast for the favorite warmest country for the next 4 days
    test_generate_temperature_forecast(warmest_country, 4)

if __name__ == "__main__":
    test_get_countries_by_continent() #Test getting all countries
    test_get_countries_by_continent("South America") # Test getting countries by continent
    test_get_countries_by_continent("North America")
    test_get_countries_by_continent("Europe")
    test_get_countries_by_continent("Africa")
    test_get_countries_by_continent("Asia")
    test_get_country_details("Brazil") # Test getting country details
    test_get_country_details("Belgium")
    test_get_country_details("USA")
    test_get_country_details("gErmaNY")
    test_get_current_temperature("Belgium") # Test getting current temperature of a country
    test_get_current_temperature("Turkey")
    test_get_current_temperature("China")
    favourite('France')
    test_favorite_unfavorite("Poland") # Test favoriting/unfavoriting a country
    test_generate_temperature_forecast("Brazil", 3)  # Test generating temperature forecast
    test_generate_temperature_forecast("Turkey", 2)
    test_generate_temperature_forecast("Belgium", 5)
    favorite_warmest_country_in_south_america()  # Favorite warmest country in South America
