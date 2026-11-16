from hashlib import sha256
import os
from pathlib import Path
import shutil
import subprocess
import sys
from sysconfig import get_config_var, get_platform
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile


PROJETO = Path(__file__).resolve().parent
FERRAMENTAS = PROJETO.parent / "ferramentas-ocr"
MODELOS_EASYOCR = (
    (
        "craft_mlt_25k.pth",
        "https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip",
        "4a5efbfb48b4081100544e75e1e2b57f8de3d84f213004b14b85fd4b3748db17",
    ),
    (
        "english_g2.pth",
        "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip",
        "e2272681d9d67a04e2dff396b6e95077bc19001f8f6d3593c307b9852e1c29e8",
    ),
)


def localizar_tesseract():
    local = FERRAMENTAS / "tesseract" / "tesseract.exe"
    if local.is_file():
        return local

    no_path = shutil.which("tesseract")
    if no_path:
        return Path(no_path)

    for variavel in ("ProgramFiles", "ProgramFiles(x86)"):
        pasta = os.environ.get(variavel)
        if pasta:
            instalado = Path(pasta) / "Tesseract-OCR" / "tesseract.exe"
            if instalado.is_file():
                return instalado
    return None


def preparar_tesseract():
    executavel = localizar_tesseract()
    if executavel is None:
        winget = shutil.which("winget")
        if winget is None:
            raise SystemExit(
                "O WinGet não está disponível. Instale o Tesseract com o idioma inglês "
                "e rode instalar.py novamente. https://tesseract-ocr.github.io/tessdoc/Installation#windows"
            )
        FERRAMENTAS.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [winget, "install", "--id", "UB-Mannheim.TesseractOCR", "--exact", "--source", "winget",
             "--location", str(FERRAMENTAS / "tesseract")],
            check=True,
        )
        executavel = localizar_tesseract()
        if executavel is None:
            raise SystemExit("O Tesseract foi instalado em outro local. Adicione a pasta dele ao PATH e tente novamente.")

    idiomas = subprocess.check_output([str(executavel), "--list-langs"], text=True)
    if "eng" not in idiomas.splitlines():
        raise SystemExit("O Tesseract precisa do idioma inglês (eng). Adicione esse idioma e rode instalar.py de novo.")


def preparar_easyocr(python):
    pasta = FERRAMENTAS / "easyocr" / "model"
    pasta.mkdir(parents=True, exist_ok=True)
    curl = shutil.which("curl.exe")
    if curl:
        # Usa os certificados do Windows e confere os modelos antes de carregá-los.
        for nome, url, assinatura in MODELOS_EASYOCR:
            destino = pasta / nome
            if destino.is_file() and sha256(destino.read_bytes()).hexdigest() == assinatura:
                continue

            print(f"Baixando {nome}...", flush=True)
            with TemporaryDirectory(dir=pasta) as temporaria:
                arquivo_zip = Path(temporaria) / "modelo.zip"
                candidato = Path(temporaria) / nome
                subprocess.run(
                    [curl, "--fail", "--location", "--silent", "--show-error", "--retry", "2",
                     "--proto", "=https", "--proto-redir", "=https", "--output", str(arquivo_zip), url],
                    check=True,
                )
                with ZipFile(arquivo_zip) as pacote, pacote.open(nome) as origem, candidato.open("wb") as saida:
                    shutil.copyfileobj(origem, saida)
                if sha256(candidato.read_bytes()).hexdigest() != assinatura:
                    raise SystemExit(f"O modelo {nome} está diferente da versão publicada. Rode o instalador novamente.")
                candidato.replace(destino)

    codigo = "from ocr_easyocr import criar_leitor; criar_leitor()"
    subprocess.run([python, "-B", "-c", codigo], cwd=PROJETO, check=True)


def main():
    if os.name != "nt":
        raise SystemExit("Este instalador foi preparado para Windows.")
    versao = sys.version_info[:2]
    if (sys.implementation.name != "cpython" or get_platform() != "win-amd64"
            or not (3, 10) <= versao <= (3, 13) or get_config_var("Py_GIL_DISABLED")):
        raise SystemExit("Use a versão padrão do Python 3.10 a 3.13 para Windows de 64 bits (x64).")

    print("1/3 Preparando as bibliotecas do Python...", flush=True)
    ambiente = PROJETO / ".venv"
    subprocess.run([sys.executable, "-m", "venv", str(ambiente)], check=True)
    python = str(ambiente / "Scripts" / "python.exe")
    pip = [python, "-m", "pip", "install", "--index-url", "https://pypi.org/simple"]
    subprocess.run(pip + ["--upgrade", "pip"], check=True)

    # Baixa os dois pacotes de CPU do PyTorch e busca as outras bibliotecas no PyPI.
    tag = f"cp{versao[0]}{versao[1]}"
    base = "https://download.pytorch.org/whl/cpu"
    torch = f"torch @ {base}/torch-2.6.0%2Bcpu-{tag}-{tag}-win_amd64.whl"
    torchvision = f"torchvision @ {base}/torchvision-0.21.0%2Bcpu-{tag}-{tag}-win_amd64.whl"
    subprocess.run(pip + [torch, torchvision, "-r", str(PROJETO / "requirements.txt")], check=True)

    print("2/3 Preparando o Tesseract...", flush=True)
    preparar_tesseract()

    print("3/3 Preparando os modelos do EasyOCR...", flush=True)
    preparar_easyocr(python)

    print("Instalação concluída. Use os comandos abaixo na pasta dos scripts.")
    print(r".\.venv\Scripts\python.exe ocr_tesseract.py")
    print(r".\.venv\Scripts\python.exe ocr_easyocr.py")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError, BadZipFile, KeyError) as erro:
        raise SystemExit(f"A instalação foi interrompida. Confira a mensagem da etapa acima.\n{erro}") from None
