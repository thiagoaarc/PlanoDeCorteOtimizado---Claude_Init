# Plano de Corte Otimizado

Aplicativo desktop em PyQt6 para criacao e analise de planos de corte de chapas industriais. O foco agora e entregar um fluxo completo: cadastro de materiais, otimizacao com multiplas heuristicas, visualizacao interativa e exportacao profissional.

## Destaques
- Interface dark moderna com acoes rapidas, abas tematicas e visual interativo em tempo real.
- Biblioteca de heuristicas (FFD, Guillotine, Skyline, Shelf, MaxRects) com avaliacao automatica para escolher a melhor estrategia.
- Relatorios PDF e SVG de alta qualidade com resumo de aproveitamento por chapa.
- Persistencia com historico e backups automaticos na pasta `data/`.
- Suporte a diferentes formatos de pecas (retangulares, circulares e poligonais regulares) com prioridades e quantidades.

## Requisitos
- Python 3.10+
- Qt 6 (PyQt6)
- ReportLab e svgwrite para exportacao
- numpy e jsonschema

Instale dependencias com:
```bash
pip install -r requirements.txt
```

## Como executar
```bash
python Main.py
```

## Fluxo recomendado
1. Cadastre chapas (aba "Chapas") definindo dimensoes, quantidade e margem.
2. Cadastre pecas (aba "Pecas") escolhendo formato e parametros especificos.
3. Na aba "Estrategia" escolha o algoritmo, defina kerf/margem e execute. Opcionalmente use "Comparar algoritmos" para deixar o sistema selecionar a melhor heuristica automaticamente.
4. Visualize o resultado na aba "Visualizacao" (zoom, ajuste automatizado e exportacao).
5. Salve ou carregue inventarios completos a partir dos botoes na barra superior.

## Testes
Os testes unitarios continuam em `tests/`. Execute-os com:
```bash
pytest
```

## Roadmap sugerido
- Simulacao de custos e metricas financeiras por chapa.
- Otimizacao multi-thread e execucao em lote.
- Editor de defeitos visuais diretamente na aba de chapas.
- Perfil de materiais, integracao com maquinas CNC e formatos personalizados.

