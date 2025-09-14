def extract_unique_item_metadata(item_info):
    formatted_data = {
        "name": item_info.get("name"),
        "base_type": item_info.get("baseType"),
        "item_level": item_info.get("ilvl"),
        "icon": item_info.get("icon"),
        "properties": {},
        "implicit_mods": [],
        "explicit_mods": [],
        "flavor_text": "\n".join(item_info.get("flavourText", []))
        if item_info.get("flavourText")
        else None,
        "requirements": {},
        "description": item_info.get("descrText"),
    }

    # Process properties
    for prop in item_info.get("properties", []):
        # Handle property name formatting
        clean_name = prop["name"]
        # Remove square brackets from property names
        clean_name = clean_name.replace("[", "").replace("]", "")

        # For property names with "or" separated values, take the second value
        if "|" in clean_name:
            clean_name = clean_name.split("|")[-1]

        # Remove all colons from the name
        clean_name = clean_name.replace(":", "").strip()
        if prop.get("values"):
            value = prop["values"][0][0]
            if "|" in value:
                value = value.split("|")[-1]
            formatted_data["properties"][clean_name] = value
        else:
            # Store name without colon for properties without values
            formatted_data["properties"][clean_name] = None

    # Process explicit requirements
    for req in item_info.get("requirements", []):
        if "|" in req["name"]:
            clean_name = req["name"].split("|")[-1].rstrip("]").lstrip("[")
        else:
            clean_name = req["name"]

        if req.get("values"):
            formatted_data["requirements"][clean_name] = req["values"][0][0]

    # Add level 64 requirement for all relics
    if "Relic" in item_info.get("baseType", ""):
        formatted_data["requirements"]["Level"] = "64"

    # Get the mods
    implicit_mods = item_info.get("implicitMods", [])
    explicit_mods = item_info.get("explicitMods", [])

    # Collect all ranges with their target mod indices
    implicit_ranges = {}
    explicit_ranges = {}

    if "extended" in item_info and "mods" in item_info["extended"]:
        if "sanctum" in item_info["extended"]["mods"]:
            # Handle sanctum mods (same as before)
            explicit_mods_mapping = {}
            for i, hash_entry in enumerate(
                item_info["extended"]["hashes"].get("sanctum", [])
            ):
                hash_id = hash_entry[0]
                explicit_mod_index = hash_entry[1][0]
                explicit_mods_mapping[explicit_mod_index] = i

            for i, mod in enumerate(item_info["extended"]["mods"]["sanctum"]):
                if mod and "magnitudes" in mod and mod["magnitudes"]:
                    for magnitude in mod["magnitudes"]:
                        if i in explicit_mods_mapping:
                            target_index = explicit_mods_mapping[i]
                            explicit_ranges[target_index] = {
                                "min": magnitude["min"],
                                "max": magnitude["max"],
                            }
        else:
            # Handle implicit mods
            implicit_mods_mapping = {}
            if "implicit" in item_info["extended"]["hashes"]:
                for i, hash_entry in enumerate(
                    item_info["extended"]["hashes"]["implicit"]
                ):
                    hash_id = hash_entry[0]
                    implicit_mod_index = hash_entry[1][0]
                    implicit_mods_mapping[implicit_mod_index] = i

                for i, mod in enumerate(
                    item_info["extended"]["mods"].get("implicit", [])
                ):
                    if mod and "magnitudes" in mod and mod["magnitudes"]:
                        for magnitude in mod["magnitudes"]:
                            if i in implicit_mods_mapping:
                                target_index = implicit_mods_mapping[i]
                                implicit_ranges[target_index] = {
                                    "min": magnitude["min"],
                                    "max": magnitude["max"],
                                }

            # Handle explicit mods
            explicit_mods_mapping = {}
            for i, hash_entry in enumerate(
                item_info["extended"]["hashes"].get("explicit", [])
            ):
                hash_id = hash_entry[0]
                explicit_mod_index = hash_entry[1][0]
                explicit_mods_mapping[explicit_mod_index] = i

            for i, mod in enumerate(item_info["extended"]["mods"].get("explicit", [])):
                if mod and "magnitudes" in mod and mod["magnitudes"]:
                    for magnitude in mod["magnitudes"]:
                        if i in explicit_mods_mapping:
                            target_index = explicit_mods_mapping[i]
                            explicit_ranges[target_index] = {
                                "min": magnitude["min"],
                                "max": magnitude["max"],
                            }

    # Process implicit mods with ranges
    for i, mod in enumerate(implicit_mods):
        clean_mod = mod
        while "[" in clean_mod and "]" in clean_mod:
            start = clean_mod.find("[")
            end = clean_mod.find("]") + 1
            formatted_text = clean_mod[start:end].split("|")[-1].rstrip("]").lstrip("[")
            clean_mod = clean_mod[:start] + formatted_text + clean_mod[end:]

        if i in implicit_ranges:
            import re

            number_match = re.search(r"\d+", clean_mod)
            if number_match:
                range_text = (
                    f"({implicit_ranges[i]['min']}-{implicit_ranges[i]['max']})"
                )
                clean_mod = (
                    clean_mod[: number_match.start()]
                    + range_text
                    + clean_mod[number_match.end() :]
                )

        formatted_data["implicit_mods"].append(clean_mod)

    # Process explicit mods with ranges
    for i, mod in enumerate(explicit_mods):
        clean_mod = mod
        while "[" in clean_mod and "]" in clean_mod:
            start = clean_mod.find("[")
            end = clean_mod.find("]") + 1
            formatted_text = clean_mod[start:end].split("|")[-1].rstrip("]").lstrip("[")
            clean_mod = clean_mod[:start] + formatted_text + clean_mod[end:]

        if i in explicit_ranges:
            magnitude = explicit_ranges[i]
            if not (magnitude["min"] == "1" and magnitude["max"] == "1"):
                import re

                number_match = re.search(r"-?\d+", clean_mod)
                if number_match:
                    range_text = f"({magnitude['min']}-{magnitude['max']})"
                    mod_prefix = clean_mod[: number_match.start()].rstrip("-")
                    clean_mod = (
                        mod_prefix + range_text + clean_mod[number_match.end() :]
                    )

        formatted_data["explicit_mods"].append(clean_mod)

    return formatted_data
