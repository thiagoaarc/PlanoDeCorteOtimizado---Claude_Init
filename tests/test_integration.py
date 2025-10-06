import pytest

from data.version_control import VersionControl
from models.chapa import Chapa
from models.peca import Peca
from services.optimization import ffd_packing, guillotine_packing


def test_workflow_completo():
    chapa = Chapa(id="C1", w=1000, h=1000, qtd=1)
    pecas = [
        Peca(id="P1", shape="rect", params={"w": 100, "h": 200}, qtd=2),
        Peca(id="P2", shape="circ", params={"raio": 50}, qtd=3),
    ]

    layouts, nao_alocadas = ffd_packing([chapa], pecas)
    assert len(layouts) == 1
    assert len(nao_alocadas) == 0

    assert sum(len(layout) for layout in layouts) > 0


def test_diferentes_algoritmos():
    chapa = Chapa(id="C1", w=1000, h=1000, qtd=1)
    pecas = [Peca(id="P1", shape="rect", params={"w": 100, "h": 100}, qtd=4)]

    layouts_ffd, _ = ffd_packing([chapa], pecas)
    layouts_guillotine, _ = guillotine_packing([chapa], pecas)

    assert sum(len(layout) for layout in layouts_ffd) == 4
    assert sum(len(layout) for layout in layouts_guillotine) == 4
