from typing import Optional

from pydantic import BaseModel

class PoeItemProperty(BaseModel):
    name: str
    values: list[list[str|int]]
    display_mode: Optional[int]
    type: Optional[int]

class PoeItem(BaseModel):
    realm: str
    verified: bool
    w: int #BaseItemType.Width
    h: int #BaseItemType.Height
    icon: str #Ignore for now. Empty string
    name: str #
    type_line: str
    base_type: str
    identified: bool
    ilvl: int
    descr_text: str
    flavour_text: str
    frame_type_id: str
    explicit_mods: Optional[list[str]]
    properties: Optional[list[PoeItemProperty]]
    item_level: Optional[int]
    rarity: Optional[str]
    support: Optional[bool]
    stack_size: Optional[int]
    max_stack_size: Optional[int]
    icon_tier_text: Optional[str]
