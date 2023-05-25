import requests
import json

class WikiTreeAPI:
    def __init__(self):
        self.base_url = "https://api.wikitree.com/api.php"

    def fetch_family_tree_data(self, individual1, individual2):
        data1, filename1 = self.fetch_ancestors(individual1)
        data2, filename2 = self.fetch_ancestors(individual2)
        if not data1 or not data2:
            return None
        return data1[0]['ancestors'], data2[0]['ancestors'], filename1, filename2

    def fetch_ancestors(self, individual_id):
        params = {
            "action": "getAncestors",
            "format": "json",
            "key": individual_id,
            "depth": 4
        }
        response = requests.get(self.base_url, params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred while fetching ancestors for {individual_id}: {err}")
            return None
        data = response.json()

        filename = f"ancestors_{individual_id}.txt"
        with open(filename, 'w') as file:
            json.dump(data, file)
        return data, filename

