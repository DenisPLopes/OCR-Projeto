import pytesseract # Importando a Biblioteca tesseract

from instalar import localizar_tesseract
from processamento import ALFABETO, ler_argumentos, limpar_texto, processar_lote # Importando do arquivo processamento.py

# Usa o PSM 8 para ler a faixa da placa como uma única palavra
def reconhecer(imagem):
    config = f"--oem 3 --psm 8 -c tessedit_char_whitelist={ALFABETO}"
    texto = pytesseract.image_to_string(imagem, config=config)
    return limpar_texto(texto)

# Localiza o Tesseract e roda o OCR em todas as fotos da pasta.
def main():
    args = ler_argumentos()
    executavel = localizar_tesseract()
    if executavel is not None:
        pytesseract.pytesseract.tesseract_cmd = str(executavel)

    try:
        processar_lote(args.dataset, "tesseract", reconhecer)
    except pytesseract.TesseractNotFoundError:
        raise SystemExit("Tesseract OCR não encontrado. Instale o programa e coloque a pasta dele no PATH.") from None


if __name__ == "__main__":
    main()
