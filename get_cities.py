# get_cities.py
# this is a helper function to print out the list of cities for inclusion in const.py
import requests

headers = {
    "Accept-Encoding": "gzip",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
}
url = f"https://www.metservice.com/publicData/webdata/towns-cities"
session = requests.Session()
response = session.get(url, headers=headers)
cities = response.json()["layout"]["search"]

for island in cities["searchLocations"]:
    # print(island["title"])
    for region in island["items"]:
        # print(region["heading"]["label"])
        for city in region["children"]:
            # print(city["label"])
            print(
                '{"label": "'
                + city["label"]
                + '", "value": "'
                + city["url"].split("/")[-1]
                + '"},'
            )
