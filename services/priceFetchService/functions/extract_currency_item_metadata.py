def extract_currency_item_metadata(item_info):
    formatted_data = {
        "name": item_info.get("typeLine"),
        "base_type": item_info.get("baseType"),
        "icon": item_info.get("icon"),
        "stack_size": 1,
        "max_stack_size": item_info.get("maxStackSize"),
        "description": item_info.get("descrText"),
        "effect": [],
    }

    # Clean up the description text by removing bracketed metadata
    if formatted_data["description"]:
        description = formatted_data["description"]
        while "[" in description and "]" in description:
            start = description.find("[")
            end = description.find("]") + 1
            formatted_text = (
                description[start:end].split("|")[-1].rstrip("]").lstrip("[")
            )
            description = description[:start] + formatted_text + description[end:]
        formatted_data["description"] = description

    # Get the currency effects from explicitMods
    if item_info.get("explicitMods"):
        # Process each explicit mod as a separate effect
        for effect in item_info["explicitMods"]:
            clean_effect = effect
            while "[" in clean_effect and "]" in clean_effect:
                start = clean_effect.find("[")
                end = clean_effect.find("]") + 1
                formatted_text = (
                    clean_effect[start:end].split("|")[-1].rstrip("]").lstrip("[")
                )
                clean_effect = (
                    clean_effect[:start] + formatted_text + clean_effect[end:]
                )
            formatted_data["effect"].append(clean_effect)
    
    if item_info.get("secDescrText"):
        lineageDescription = item_info["secDescrText"]
        while "[" in lineageDescription and "]" in lineageDescription:
            start = lineageDescription.find("[")
            end = lineageDescription.find("]") + 1
            formatted_text = (
                lineageDescription[start:end].split("|")[-1].rstrip("]").lstrip("[")
            )
            lineageDescription = (
                lineageDescription[:start] + formatted_text + lineageDescription[end:]
            )
        formatted_data["effect"] = []
        formatted_data["effect"].append(lineageDescription)
    
    return formatted_data
