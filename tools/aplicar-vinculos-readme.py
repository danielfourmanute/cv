#!/usr/bin/env python3
"""Aplica as datas de vínculo da CTPS no README.md e no PROJETOS.md do repositório cv."""
from pathlib import Path

MUDANCAS = [
    (
        Path("/home/ubuntu/cvwork/repo/README.md"),
        "e, desde 01/08/2019, proprietário da **DJT Sistemas**, atividade exercida em paralelo ao vínculo CLT.",
        "e, desde 01/08/2019, proprietário da **DJT Sistemas**, atividade exercida em paralelo aos vínculos "
        "CLT: Vieli Consultoria Industrial de 01/11/2017 a 18/04/2021 e, desde 19/04/2021, Móveis Weihermann S.A.",
    ),
    (
        Path("/home/ubuntu/cvwork/repo/README.md"),
        "**atuação via DJT Sistemas · em aberto** · São Bento do Sul/SC",
        "**19/04/2021 – até o momento (vínculo registrado em carteira de trabalho)** · São Bento do Sul/SC",
    ),
    (
        Path("/home/ubuntu/cvwork/repo/README.md"),
        "**11/2017 – em aberto (CLT)** · São Bento do Sul/SC · CBO 212405",
        "**01/11/2017 – 18/04/2021 (CLT)** · São Bento do Sul/SC · CBO 212405",
    ),
    (
        Path("/home/ubuntu/cvwork/repo/README.md"),
        "**08/2001 – 06/2002** · São Bento do Sul/SC · CBO 8420",
        "**01/08/2001 – 19/06/2002** · São Bento do Sul/SC · CBO 8420",
    ),
    (
        Path("/home/ubuntu/cvwork/repo/README.md"),
        "**1994 – 1995** · São Bento do Sul/SC\n\n"
        "- Operador de máquinas de processamento de dados na **Muricy Infor** (treinamento, desenvolvimento e "
        "assessoria em informática) e rotinas administrativas — primeiro contato profissional com sistema de "
        "informação.",
        "**01/02/1994 – 30/06/1995** · São Bento do Sul/SC\n\n"
        "- **Paulo Roberto Scheide** (01/02/1994 – 15/04/1994, anotado como primeiro emprego) e **Muricy Infor** "
        "(19/04/1994 – 01/09/1994), na função 34290 — operadores de máquinas de processamento de dados; "
        "nova passagem pela Scheide entre 01/03/1995 e 30/06/1995. Rotinas administrativas e de processamento: "
        "primeiro contato profissional com sistema de informação.",
    ),
    (
        Path("/home/ubuntu/cvwork/repo/PROJETOS.md"),
        "Atuação na Móveis Weihermann S.A.",
        "Atuação na Móveis Weihermann S.A. (vínculo registrado em carteira de trabalho desde 19/04/2021)",
    ),
]


def main() -> None:
    for arq, de, para in MUDANCAS:
        s = arq.read_text(encoding="utf-8")
        if de not in s:
            print(f"[pulando] {arq.name}: âncora ausente → {de[:60]!r}")
            continue
        arq.write_text(s.replace(de, para, 1), encoding="utf-8")
        print(f"[ok] {arq.name}: {de[:52]!r}")


if __name__ == "__main__":
    main()
