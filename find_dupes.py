import json

with open("jellyfin_data.json", "r") as f:
    jellyfin_data = json.load(f)

for item1 in jellyfin_data:
    for item2 in jellyfin_data:
        if item1 == item2:
            continue
        if item1['Name'] == item2['Name'] and item1['Artists'] == item2['Artists'] and item1['Album'] == item2['Album']:
            print(item1['Name'] + " - " + str(item1['Artists']))