from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Defeito:
    tipo: str
    params: Dict[str, Any]


@dataclass
class Chapa:
    id: str
    w: float
    h: float
    qtd: int = 1
    rebarba: float = 0
    custo: float = 0
    defeitos: List[Defeito] = field(default_factory=list)
    cliente: str = ""
    lote: str = ""
    cor: str = ""
    obs: str = ""

    _schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "w": {"type": "number", "minimum": 0},
            "h": {"type": "number", "minimum": 0},
            "qtd": {"type": "integer", "minimum": 1},
        },
        "required": ["id", "w", "h"],
    }

    def __post_init__(self):
        if self.w <= 0 or self.h <= 0:
            raise ValueError("Dimensoes da chapa devem ser positivas")
        if self.qtd <= 0:
            raise ValueError("Quantidade deve ser positiva")

    @property
    def area(self) -> float:
        return self.w * self.h

    @property
    def area_util(self) -> float:
        return max(0.0, (self.w - 2 * self.rebarba) * (self.h - 2 * self.rebarba))

    def to_dict(self) -> Dict[str, Any]:
        """Converte a chapa para um dicionario serializavel."""
        return {
            "id": self.id,
            "w": self.w,
            "h": self.h,
            "qtd": self.qtd,
            "rebarba": self.rebarba,
            "custo": self.custo,
            "defeitos": [{"tipo": defeito.tipo, "params": defeito.params} for defeito in self.defeitos],
            "cliente": self.cliente,
            "lote": self.lote,
            "cor": self.cor,
            "obs": self.obs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chapa":
        """Cria instancia a partir de um dicionario."""
        defeitos = [Defeito(item["tipo"], item["params"]) for item in data.get("defeitos", [])]
        return cls(
            id=data["id"],
            w=data["w"],
            h=data["h"],
            qtd=data.get("qtd", 1),
            rebarba=data.get("rebarba", 0),
            custo=data.get("custo", 0),
            defeitos=defeitos,
            cliente=data.get("cliente", ""),
            lote=data.get("lote", ""),
            cor=data.get("cor", ""),
            obs=data.get("obs", ""),
        )
