# OCR de placas veiculares

Projeto desenvolvido em Python para a atividade de Processamento Digital de Imagens.

O objetivo é detectar placas nas fotos e comparar a leitura dos caracteres com Tesseract e EasyOCR. Os dois usam o mesmo recorte.

## Requisitos

- Windows de 64 bits (x64) e Python 3.10 ou 3.11.
- Acesso à internet para a primeira instalação.
- Imagens da pasta `placas_exercício` fornecida na atividade.

## Como executar

1. Baixe e extraia os arquivos do repositório.
2. Na sua cópia local, coloque a pasta `placas_exercício` ao lado de `placas-ocr`.
3. Abra o PowerShell dentro de `placas-ocr`, onde está o arquivo `instalar.py`.
4. Rode o instalador e aguarde a conclusão.

   ```powershell
   python instalar.py
   ```

5. No mesmo PowerShell, execute os dois scripts.

   ```powershell
   .\.venv\Scripts\python.exe ocr_tesseract.py
   .\.venv\Scripts\python.exe ocr_easyocr.py
   ```

O instalador atualiza o pip, instala as bibliotecas e baixa os modelos do EasyOCR. O EasyOCR usa o PyTorch para rodar esses modelos. Se for preciso instalar o Tesseract, o instalador usa o WinGet. Se o WinGet estiver indisponível, instale o Tesseract com o idioma inglês (`eng`), adicione o programa ao `PATH` do Windows e rode o instalador de novo. [Instalação do Tesseract no Windows](https://tesseract-ocr.github.io/tessdoc/Installation#windows)

## Funcionamento

O código usa o filtro gaussiano, o Canny e os contornos para localizar a placa. Depois, corrige a perspectiva e recorta a faixa dos caracteres, seguindo os métodos trabalhados durante as aulas.

Os dois scripts testam a faixa colorida, escala de cinza, Otsu e limiar adaptativo para buscar a melhor opção. Os arquivos de texto guardam a leitura da faixa colorida, pois nos testes foi a que apresentou melhor desempenho geral.

## Resultados

Cada método gera um arquivo `.txt` por foto na pasta `resultados`. Depois de rodar os dois scripts, consulte o [resumo das leituras](placas-ocr/resultados/resumo_ocr.txt) para comparar os resultados lado a lado.

O detector recortou uma região de placa em 19 das 20 fotos. A foto 4 ficou sem detecção. Na foto 2, a placa de baixo foi escolhida pela regra do maior contorno.

| Faixa testada | Tesseract | EasyOCR |
| --- | ---: | ---: |
| Colorida | 3/20 | 2/20 |
| Escala de cinza | 3/20 | 1/20 |
| Otsu | 3/20 | 0/20 |
| Limiar adaptativo | 0/20 | 0/20 |

A tabela mostra quantas leituras completas bateram com as fotos.
