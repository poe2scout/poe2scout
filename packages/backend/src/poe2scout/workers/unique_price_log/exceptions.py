class UniqueItemDelistedError(Exception):
    def __init__(self, unique_item_id: int, item_name: str):
        self.unique_item_id = unique_item_id
        self.item_name = item_name
        super().__init__(f"Unique item '{item_name}' is currently delisted")
