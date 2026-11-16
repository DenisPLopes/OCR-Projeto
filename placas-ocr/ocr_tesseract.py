import pytesseract

from processamento import ALFABETO, PASTA_PROJETO, ler_argumentos, limpar_texto, processar_lote


def reconhecer(imagem):
    # O PSM 8 lê a faixa como uma única palavra.
    config = f"--oem 3 --psm 8 -c tessedit_char_whitelist={ALFABETO}"
    texto = pytesseract.image_to_string(imagem, config=config)
    return limpar_texto(texto)


def main():
    args = ler_argumentos()
    executavel = PASTA_PROJETO.parent / "ferramentas-ocr" / "tesseract" / "tesseract.exe"
    if executavel.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(executavel)

    try:
        processar_lote(args.dataset, "tesseract", reconhecer)
    except pytesseract.TesseractNotFoundError:
        raise SystemExit("Tesseract OCR não encontrado. Instale o programa e coloque a pasta dele no PATH.") from None


if __name__ == "__main__":
    main()
