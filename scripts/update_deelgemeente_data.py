import json

import requests

# URL to deelgemeenten.json
url = "https://github.com/OnroerendErfgoed/deelgemeenten/raw/refs/heads/master/data/json/deelgemeenten.json"
response = requests.get(url)
deelgemeenten = response.json()
deelgemeenten_mapped = [
    {
        "id": deelgemeente["deelgemeente_id"],
        "naam": deelgemeente["deelgemeente_naam"],
        "gemeente_niscode": deelgemeente["gemeente_id"]
    }
    for deelgemeente in deelgemeenten
]
with open("../crabpy/data/deelgemeenten.json", "w") as deelgemeenten_file:
    json.dump(deelgemeenten_mapped, deelgemeenten_file, indent=2)

