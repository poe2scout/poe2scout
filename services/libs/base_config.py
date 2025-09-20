from typing import get_type_hints, Type, TypeVar
import os
from pydantic import BaseModel

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseModel):
    @classmethod
    def load_from_env(cls: Type[T]) -> T:
        """
        Creates an instance of the config class, loading values from environment variables.
        Field names are converted to uppercase with underscores for env var names.
        Example: database_url -> DATABASE_URL
        """
        # Get all fields and their types from the class
        field_types = get_type_hints(cls)

        # Build the config data from environment variables
        config_data = {}
        for field_name, field_type in field_types.items():
            env_name = field_name.upper()
            env_value = os.getenv(env_name)

            if env_value is None:
                # Check if the field has a default value in the model
                if field_name in cls.model_fields:
                    field_info = cls.model_fields[field_name]
                    if field_info.default is not None:
                        config_data[field_name] = field_info.default
                        continue
                    elif not field_info.is_required():
                        continue
                raise ValueError(f"Required environment variable {env_name} not set")

            # Convert the string value to the correct type
            try:
                if field_type == bool:
                    config_data[field_name] = env_value.lower() in ("true", "1", "yes")
                elif field_type == list:
                    config_data[field_name] = env_value.split(",")
                else:
                    config_data[field_name] = field_type(env_value)
            except ValueError as e:
                raise ValueError(f"Failed to parse {env_name}: {str(e)}")

        return cls(**config_data)
