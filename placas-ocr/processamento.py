from argparse import ArgumentParser
from pathlib import Path
import re

import cv2
import numpy as np


PASTA_PROJETO = Path(__file__).resolve().parent
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def extrair_placa(imagem):
    # Bordas e contornos, como no exemplo placa_automatica.py.
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    suavizada = cv2.GaussianBlur(cinza, (5, 5), 0)
    bordas = cv2.Canny(suavizada, 90, 220)
    bordas = cv2.dilate(bordas, np.ones((3, 3), np.uint8), iterations=1)
    contornos, _ = cv2.findContours(bordas, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Escolhe o maior quadrilátero com área e proporção de placa.
    candidatos = []
    altura, largura = imagem.shape[:2]
    for contorno in contornos:
        perimetro = cv2.arcLength(contorno, True)
        poligono = cv2.approxPolyDP(contorno, 0.025 * perimetro, True)
        if len(poligono) != 4 or not cv2.isContourConvex(poligono):
            continue
        _, _, w, h = cv2.boundingRect(poligono)
        proporcao = w / max(h, 1)
        area = cv2.contourArea(poligono)
        if not (2.0 <= proporcao <= 12.0):
            continue
        if not (0.015 * largura * altura <= area <= 0.55 * largura * altura):
            continue
        candidatos.append((area, poligono))

    if not candidatos:
        return None

    candidatos.sort(key=lambda item: item[0], reverse=True)
    poligono = candidatos[0][1]

    # Ordena os quatro cantos e corrige a perspectiva.
    pontos = poligono.reshape(4, 2).astype(np.float32)
    soma = pontos.sum(axis=1)
    diferenca = np.diff(pontos, axis=1).ravel()
    origem = np.array([
        pontos[np.argmin(soma)], pontos[np.argmin(diferenca)],
        pontos[np.argmax(soma)], pontos[np.argmax(diferenca)],
    ], dtype=np.float32)
    destino = np.array([[0, 0], [599, 0], [599, 219], [0, 219]], dtype=np.float32)
    matriz = cv2.getPerspectiveTransform(origem, destino)
    return cv2.warpPerspective(imagem, matriz, (600, 220))


def preparar_placa(placa):
    # Aplica os pré-processamentos da aula à mesma faixa dos caracteres.
    faixa = placa[55:205, 48:590]
    cinza = cv2.cvtColor(faixa, cv2.COLOR_BGR2GRAY)
    _, otsu = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptativo = cv2.adaptiveThreshold(
        cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    return {"colorida": faixa, "cinza": cinza, "otsu": otsu, "adaptativo": adaptativo}


def limpar_texto(texto):
    return re.sub(r"[^A-Z0-9]", "", texto.upper())


def ler_argumentos():
    dataset = PASTA_PROJETO.parent / "placas_exercício"
    if not dataset.is_dir():
        dataset = PASTA_PROJETO / "placas_exercício"

    parser = ArgumentParser()
    parser.add_argument("dataset", nargs="?", type=Path, default=dataset)
    return parser.parse_args()


def processar_lote(dataset, metodo, reconhecer):
    arquivos = sorted(
        arquivo for arquivo in dataset.rglob("*")
        if arquivo.is_file() and arquivo.suffix.lower() in (".jpg", ".jpeg", ".png")
    )
    if not arquivos:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em {dataset}.")

    saida = PASTA_PROJETO / "resultados" / metodo
    saida.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos:
        # A pasta do dataset contém acento no nome.
        dados = np.frombuffer(arquivo.read_bytes(), dtype=np.uint8)
        imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR) if dados.size else None
        if imagem is None:
            texto = "IMAGEM INVÁLIDA"
        else:
            placa = extrair_placa(imagem)
            if placa is None:
                texto = "SEM PLACA DETECTADA"
            else:
                leituras = {}
                for nome, variante in preparar_placa(placa).items():
                    leituras[nome] = reconhecer(variante)
                    print(f"{arquivo.name} | {nome}: {leituras[nome]}")

                texto = leituras["colorida"] or "SEM LEITURA"

        destino = saida / f"{arquivo.stem}_{metodo}.txt"
        destino.write_text(texto + "\n", encoding="utf-8", newline="\n")

    salvar_resumo(arquivos)


def salvar_resumo(arquivos):
    if all(arquivo.stem.isdecimal() for arquivo in arquivos):
        arquivos = sorted(arquivos, key=lambda arquivo: int(arquivo.stem))

    pasta = PASTA_PROJETO / "resultados"
    linhas = [("Imagem", "Tesseract", "EasyOCR")]

    # Monta a tabela quando os resultados dos dois métodos estiverem disponíveis.
    for arquivo in arquivos:
        leituras = []
        for metodo in ("tesseract", "easyocr"):
            destino = pasta / metodo / f"{arquivo.stem}_{metodo}.txt"
            try:
                leitura = destino.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                return
            if not leitura:
                return
            leituras.append(leitura)
        linhas.append((arquivo.name, *leituras))

    larguras = [max(len(texto) for texto in coluna) for coluna in zip(*linhas)]
    tabela = [
        " | ".join(texto.ljust(largura) for texto, largura in zip(linha, larguras)).rstrip()
        for linha in linhas
    ]
    tabela.insert(1, "-+-".join("-" * largura for largura in larguras))
    resumo = pasta / "resumo_ocr.txt"
    resumo.write_text("\n".join(tabela) + "\n", encoding="utf-8", newline="\n")
