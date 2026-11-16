# OCR de placas veiculares

Atividade de Processamento Digital de Imagens. O projeto procura a placa nas fotos e recorta a região encontrada. Depois, usa Tesseract e EasyOCR para comparar a leitura dos caracteres na mesma faixa da placa.

## 1. Organize as pastas

Baixe o projeto e extraia os arquivos. Deixe a pasta `placas_exercício`, com as imagens fornecidas na atividade, ao lado da pasta do projeto. A estrutura fica assim.

```text
Atividade Final/
  OCR-Projeto/       (códigos e requirements.txt)
  placas_exercício/ (imagens da atividade)
```

O nome da pasta do projeto pode variar. A pasta `placas_exercício` precisa manter esse nome para a busca automática.

## 2. Instale as dependências no Windows

Instale o Python 3.10 de 64 bits e o Tesseract OCR com o idioma inglês (`eng`). Adicione a pasta do Tesseract ao `PATH` do Windows e abra um novo PowerShell. [Instalação do Tesseract no Windows](https://tesseract-ocr.github.io/tessdoc/Installation#windows)

Abra o PowerShell dentro da pasta que tem os arquivos `.py` e `requirements.txt`. Os comandos abaixo instalam as bibliotecas do projeto e o PyTorch para CPU.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Rode os dois scripts

```powershell
.\.venv\Scripts\python.exe ocr_tesseract.py
.\.venv\Scripts\python.exe ocr_easyocr.py
```

Na primeira execução, o EasyOCR pode demorar um pouco para baixar os modelos. Se você guardou as fotos em outra pasta, passe o caminho entre aspas depois do nome do script, nos dois comandos.

Na cópia preparada em Downloads, mantenha `ferramentas-ocr` ao lado de `placas-ocr`. Com as bibliotecas já instaladas, nessa cópia basta rodar `python ocr_tesseract.py` e depois `python ocr_easyocr.py`.

## 4. Confira os resultados

O Tesseract grava em `resultados/tesseract/` e o EasyOCR em `resultados/easyocr/`. Cada foto tem um arquivo por método, como `1_tesseract.txt` e `1_easyocr.txt`. Depois de rodar os dois scripts, abra `resultados/resumo_ocr.txt` para ver as leituras lado a lado.

## Comparação

A detecção segue o exemplo `placa_automatica.py`, com os limiares do Canny e a proporção máxima ajustados para as fotos da atividade. Os dois scripts mostram no terminal as leituras com quatro formas de preparar a mesma faixa da placa. A leitura da faixa colorida é a que vai para os arquivos de texto.

| Faixa usada no OCR | Tesseract | EasyOCR |
| --- | ---: | ---: |
| Colorida | 3/20 | 2/20 |
| Escala de cinza | 3/20 | 1/20 |
| Otsu | 3/20 | 0/20 |
| Limiar adaptativo | 0/20 | 0/20 |

A tabela conta as leituras completas que conferem com as fotos. O detector encontrou uma região de placa em 19 das 20 imagens. A foto 4 ficou sem detecção. Na foto 2, o detector escolheu a placa de baixo pela regra do maior contorno.
