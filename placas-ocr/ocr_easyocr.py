import easyocr # Importando a biblioteca easyocr

from processamento import ALFABETO, PASTA_PROJETO, ler_argumentos, limpar_texto, processar_lote # Importando do arquivo processamento.py

# Lendo a faixa da placa e juntando os trechos
def reconhecer(leitor, imagem):
    resultados = leitor.readtext(imagem, detail=1, paragraph=False, allowlist=ALFABETO)
    partes = []
    for caixa, texto, _ in resultados:
        partes.append((min(ponto[0] for ponto in caixa), texto))

    # A posição horizontal das caixas mantém os caracteres na ordem certa
    texto = "".join(texto for _, texto in sorted(partes))
    return limpar_texto(texto)

# Cria o leitor do EasyOCR e usa modelos locais quando estão disponíveis
def criar_leitor():
    pasta = PASTA_PROJETO.parent / "ferramentas-ocr" / "easyocr"
    opcoes_locais = {}
    if pasta.is_dir():
        opcoes_locais["model_storage_directory"] = str(pasta / "model")
        opcoes_locais["user_network_directory"] = str(pasta / "user_network")
    return easyocr.Reader(["en"], gpu=False, verbose=False, **opcoes_locais)

# Cria o leitor uma vez e utiliza ele para todas as fotos
def main():
    args = ler_argumentos()
    leitor = criar_leitor()
    processar_lote(args.dataset, "easyocr", lambda imagem: reconhecer(leitor, imagem))


if __name__ == "__main__":
    main()
