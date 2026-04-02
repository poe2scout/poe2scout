from pydantic import BaseModel, ConfigDict


def to_pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_"))


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        from_attributes=True,
        populate_by_name=True,
        serialize_by_alias=True,
    )
