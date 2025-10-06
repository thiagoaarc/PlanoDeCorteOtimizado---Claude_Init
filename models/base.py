from dataclasses import dataclass, field
from typing import Dict

import jsonschema


@dataclass
class ModelBase:
    id: str
    _schema: Dict = field(default_factory=dict)

    def __post_init__(self):
        if hasattr(self, "_schema"):
            self.validate()

    def validate(self) -> bool:
        try:
            jsonschema.validate(instance=self.__dict__, schema=self._schema)
            return True
        except jsonschema.exceptions.ValidationError as exc:
            raise ValueError(f"Erro de validacao: {exc}")
