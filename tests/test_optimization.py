import pytest
from models.chapa import Chapa
from models.peca import Peca
from services.optimization import ffd_packing, calc_area

def test_calc_area_rect():
    peca = Peca(id="P1", shape="rect", params={"w": 100, "h": 50}, qtd=1)
    assert calc_area(peca) == 5000

def test_ffd_packing_basic():
    chapa = Chapa(id="C1", w=1000, h=1000, qtd=1)
    peca = Peca(id="P1", shape="rect", params={"w": 100, "h": 100}, qtd=1)
    
    layouts, nao_alocadas = ffd_packing([chapa], [peca], allow_rotation=True, kerf=0)
    
    assert len(layouts) == 1
    assert len(layouts[0]) == 1
    assert len(nao_alocadas) == 0
