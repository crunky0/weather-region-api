from flask import Flask,jsonify,Response
from flask_restful import Resource, Api,reqparse
import requests
import json
import argparse

app = Flask(__name__) #creating the flask app
api = Api(app) #creating the api

#I use argparse to take 2 mandatory arguments when starting the program which are the api keys that will be used.
parser = argparse.ArgumentParser()
parser.add_argument("--weather-api-key", required=True, help="API key for OpenWeather API")
parser.add_argument("--db-api-key", required=True, help="API key for MongoDB")
args = parser.parse_args()

weather_api_key = args.weather_api_key
db_api_key = args.db_api_key

#makes a call to the rest countries api to get the name,capital and some other information about a given country
def getCountryDetails(country):
    response = requests.get(f'https://restcountries.com/v3.1/name/{country}?fields=name,capital,capitalInfo,area,population')
    data = response.json()
    return data

#since the rest countries api returns bunch of names for a country, to increase readablity this function extracts the common name for a country
def commonNameExtractor(data):
    common_name_list = [country['name']['common'] for country in data]
    return jsonify(common_name_list)

#given a list of countries this function makes several api calls to the openweather api to find the hottest country in the given region
def tempComparison(data):
    temp,country = -100,''
    
    for i in data:
        lat, lon = i['capitalInfo']['latlng']
        weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&mode=json&units=metric')
        weather_data_raw = weather_response.json()
        current_temp = float(weather_data_raw['main']['temp'])
        if(current_temp>temp):
            temp = current_temp
            country = i['name']['common']
    return temp,country

#this one is also to increase readablity. it extracts the time and temperature info for the weather forecast
def weatherForecastList(data):
    time = []
    temp = []
    for i in data['list']:
        temp.append(i['main']['temp'])
        time.append(i['dt_txt'])
    return time,temp

#it connects to my database through the MongoDB api and makes a POST request to add the name of the favourited country to the database
#I used the official documentation of the MongoDB API for the function
def favouriteCountry(name):
    url = "https://eu-central-1.aws.data.mongodb-api.com/app/data-gzlnt/endpoint/data/v1/action/insertOne"
    payload = json.dumps({
        "collection": "fav_list",
        "database": "favourite_countries",
        "dataSource": "Cluster0",
        "document": {
            "name": name
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'api-key': db_api_key,
    }
    try:
        requests.request("POST", url, headers=headers, data=payload)
        return 'Added Successfully'
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 #in case of an error throws error code 500

#same functionality but to unfavourite a country that is in the favourites list
def unfavouriteCountry(name):
    url = "https://eu-central-1.aws.data.mongodb-api.com/app/data-gzlnt/endpoint/data/v1/action/deleteOne"
    payload = json.dumps({
        "collection": "fav_list",
        "database": "favourite_countries",
        "dataSource": "Cluster0",
        "filter": {
            "name": name
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'api-key': db_api_key,
    }
    try:
        requests.request("POST", url, headers=headers, data=payload)
        return 'Deleted Successfully'
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#makes an api call to the database to retrieve the names of the favourited countries
def generateFavList():
    url = "https://eu-central-1.aws.data.mongodb-api.com/app/data-gzlnt/endpoint/data/v1/action/find"
    payload = json.dumps({
    "collection": "fav_list",
    "database": "favourite_countries",
    "dataSource": "Cluster0",
    "filter": {},  # empty filter so it returns everything on the list
    "projection": {"name": 1}, #it only shows the names of the countries
    })
    headers = {
        'Content-Type': 'application/json',
        'api-key': db_api_key,
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        name_list = [i['name'] for i in data['documents']] #to increase readablity it returns it as a name list
        return name_list
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#I used an OOP based approach for API endpoints
#All classes inherit the flask_restful.Resource class

#Simple class and with a GET endpoint the return a list of all the common names of all countries
#It makes an api call to the rest countries api
#Returns only the common names of the countries for readablity
class Countries(Resource):
    def get(self):
        try:
            response = requests.get('https://restcountries.com/v3.1/all?fields=name')
            data = response.json()
            return commonNameExtractor(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

#Same functionality but it takes a region and returns the countries that are in that region
class RegionCountries(Resource):
    def get(self,region):
        try:
            response = requests.get(f'https://restcountries.com/v3.1/region/{region}?fields=name')
            data = response.json() #response is transformed into json for parsing
            return commonNameExtractor(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

#Returns details for the given country using a different endpoint of the same api
#After that response data is edited and modified for increased readability
class CountryDetails(Resource):
    def get(self,country):
        try:
            data = getCountryDetails(country)
            lat, lon = data[0]['capitalInfo']['latlng'] # 0 because response returns a JSON array
            common_name = data[0]['name']['common']
            modified_data = {'country':common_name, 'capital':data[0]['capital'],'latitude':lat,'longtitude':lon,'area':data[0]['area'],'population':data[0]['population']}
            return jsonify(modified_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
#First a call is made to the rest countries api to get the coordinates of the countries capital's location
#After that the data is used in the weather api call to get the current weather information
#Lastly data is parsed and necessary information is extracted
class WeatherInfo(Resource):
    def get(self,country):
        try:
            data = getCountryDetails(country)
            lat, lon = data[0]['capitalInfo']['latlng']
            common_name = data[0]['name']['common']
            weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&mode=json&units=metric')
            weather_data_raw = weather_response.json()
            current_temp = weather_data_raw['main']['temp']
            current_weather = weather_data_raw['weather'][0]['main']
            weather_data_modified = {'current_temp':current_temp,'current_weather':current_weather,'country':common_name}
            return weather_data_modified

        except Exception as e:
            return jsonify({'error': str(e)}), 500
#Start is similar to the previous function however in this one another api call from the weather api is used that gives 3 hour/5 day forecast info
#After the necessary information is parsed there is another api call to the quick chart api to graph the wanted interval
class WeatherForecast(Resource):
    def get(self,country):
        parser = reqparse.RequestParser()#reqparser is used to ensure that a number of days is entered with the api request 
        parser.add_argument('days', type=int, required=True, help='Number of days to be forecasted',location ='args')
        args = parser.parse_args()
        try:
            data = getCountryDetails(country)
            lat, lon = data[0]['capitalInfo']['latlng']
            common_name = data[0]['name']['common']
            number_of_days = str((int(args['days'])*8)+1) # 3 hour intervals are taken so for each day 8 intervals are taken 
            weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}&mode=json&units=metric&cnt={number_of_days}')
            weather_data = weather_response.json()
            time,temp = weatherForecastList(weather_data)
            title_name = f"Weather forcast in {common_name} for the next {args['days']} days"
            graph = requests.get("https://quickchart.io/chart?c={type:'line',data:{labels:"+str(time)+",datasets:[{label:'Temperatures',data:"+str(temp)+"}]},options:{title:{display:true,text:'"+title_name.replace(' ', '%20')+"'}}}")
            return Response(graph.content, content_type='image/png') #turns the responde object into a png

        except Exception as e:
            return jsonify({'error': str(e)}), 500
#this get method returns the hottest country in a continent
#if all is selected as the continent it returns the hottest country in the world
class HottestCountry(Resource):
    def get(self):
        parser = reqparse.RequestParser() #reqparser is used to ensure that a region is entered with the api request 
        parser.add_argument('region', type=str, required=True, help='Enter the region that you want to find the hottest country of, to search for whole word use all',location ='args')
        args = parser.parse_args()
        regi = args['region']
        try:
            if(args['region'] == 'all'):
                response = requests.get('https://restcountries.com/v3.1/all?fields=name,capitalInfo')
                data = response.json()
                temp,country = tempComparison(data)
                return jsonify({f'Hottest country in the world is:':country,f'Temperature is:':temp})
            else:
                response = requests.get(f'https://restcountries.com/v3.1/region/{regi}?fields=name,capitalInfo')
                data = response.json()
                temp,country = tempComparison(data)
                return jsonify({f'country':country,f'temperature':temp})

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
#final class with 3 endpoints
#get function gets the currently favourited countries from the database
#post function favourites a country and adds it to the database
#delete function unfavourites a country and deletes it from the database
class Favourites(Resource):
    def get(self):
        return generateFavList()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('country', type=str, required=True, help='Name of the country to favourite',location ='args')
        args = parser.parse_args()
        data = getCountryDetails(args['country'])
        common_name = data[0]['name']['common'] 
        favouriteCountry(common_name)
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('country', type=str, required=True, help='Name of the country to unfavourite',location ='args')
        args = parser.parse_args()
        data = getCountryDetails(args['country'])
        common_name = data[0]['name']['common'] 
        unfavouriteCountry(common_name)

#finally all of the endpoints are added to the api
api.add_resource(Countries, '/countries')
api.add_resource(RegionCountries, '/countries/<string:region>')
api.add_resource(CountryDetails, '/country/<string:country>')
api.add_resource(WeatherInfo, '/weather/current/<string:country>')
api.add_resource(WeatherForecast, '/weather/forecast/<string:country>')
api.add_resource(HottestCountry, '/weather/hottest')
api.add_resource(Favourites, '/favourites')


if __name__ == '__main__':
    app.run(debug=True)





