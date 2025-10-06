from dataclasses import dataclass
from typing import Any, Dict

import math


@dataclass
class Peca:
    id: str
    shape: str
    params: Dict[str, Any]
    qtd: int = 1
    prioridade: int = 0
    cliente: str = ""
    lote: str = ""
    cor: str = ""
    obs: str = ""

    _schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "shape": {"type": "string", "enum": ["rect", "circ", "poly"]},
            "params": {"type": "object"},
            "qtd": {"type": "integer", "minimum": 1},
            "prioridade": {"type": "integer", "minimum": 0},
        },
        "required": ["id", "shape", "params", "qtd"],
    }

    def __post_init__(self):
        if self.qtd <= 0:
            raise ValueError("Quantidade deve ser positiva")
        if self.shape not in ["rect", "circ", "poly"]:
            raise ValueError("Formato deve ser 'rect', 'circ' ou 'poly'")

    @property
    def area(self) -> float:
        """Retorna a area da peca baseado na forma."""
        if self.shape == "rect":
            w = self.params.get("w", 0.0)
            h = self.params.get("h", 0.0)
            return w * h
        if self.shape == "circ":
            r = self.params.get("raio", 0.0)
            return math.pi * r * r
        if self.shape == "poly":
            n = self.params.get("n", 3)
            lado = self.params.get("lado", 0.0)
            if n >= 3 and lado > 0:
                return (n * lado * lado) / (4 * math.tan(math.pi / n))
        return 0.0

    @property
    def dimensions(self) -> Dict[str, float]:
        """Retorna dimensoes aproximadas para empacotamento."""
        if self.shape == "rect":
            return {"w": self.params.get("w", 0.0), "h": self.params.get("h", 0.0)}
        if self.shape == "circ":
            r = self.params.get("raio", 0.0)
            return {"w": 2 * r, "h": 2 * r}
        if self.shape == "poly":
            lado = self.params.get("lado", 0.0)
            return {"w": lado, "h": lado}
        return {"w": 0.0, "h": 0.0}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "shape": self.shape,
            "params": self.params,
            "qtd": self.qtd,
            "prioridade": self.prioridade,
            "cliente": self.cliente,
            "lote": self.lote,
            "cor": self.cor,
            "obs": self.obs,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Peca":
        return cls(
            id=data["id"],
            shape=data["shape"],
            params=data["params"],
            qtd=data.get("qtd", 1),
            prioridade=data.get("prioridade", 0),
            cliente=data.get("cliente", ""),
            lote=data.get("lote", ""),
            cor=data.get("cor", ""),
            obs=data.get("obs", ""),
        )
