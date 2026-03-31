import json


def create_mapping(data):
    mapping = {}

    # Process each category
    for category in data:
        for entry in category["entries"]:
            # Handle items with 'name' field (unique items)
            if "name" in entry:
                mapping[entry["name"]] = entry["text"]
            # Handle regular items
            else:
                mapping[entry["type"]] = entry["text"]

    return mapping


# Read the input file
with open("translationskr.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create the mapping
mapping = create_mapping(data)

# Write the mapping to a new file
with open("translationskrmapping.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)
