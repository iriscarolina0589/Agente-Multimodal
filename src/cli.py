"""Interfaz por linea de comandos del agente.

Ejemplos (desde la raiz del proyecto):
    python src/cli.py resumir   ruta/a/articulo.pdf
    python src/cli.py metadatos ruta/a/articulo.pdf
    python src/cli.py comparar  articulo1.pdf articulo2.pdf
    python src/cli.py chat      ruta/a/articulo.pdf
"""

import argparse

import ingest
from agent import AgenteAcademico


def resumir(agente, ruta):
    """Carga el documento y muestra su resumen por consola."""
    agente.cargar(ruta)
    r = agente.resumir()
    print("\nRESUMEN\n" + r.resumen)
    print("\nObjetivos:", *r.objetivos, sep="\n  - ")
    print("\nMetodologia:", r.metodologia)
    print("\nHallazgos:", *r.hallazgos, sep="\n  - ")
    print("\nLimitaciones:", *r.limitaciones, sep="\n  - ")


def metadatos(agente, ruta):
    """Carga el documento y muestra sus metadatos."""
    agente.cargar(ruta)
    print("\nMETADATOS")
    print(agente.extraer_entidades().model_dump_json(indent=2))


def comparar(agente, ruta_a, ruta_b):
    """Compara dos documentos y muestra la tabla resultante."""
    comp = agente.comparar(ingest.cargar_documento(ruta_a), ingest.cargar_documento(ruta_b))
    print("\nCOMPARACION")
    for aspecto, doc_a, doc_b in comp.filas():
        print(f"\n[{aspecto}]\n  A: {doc_a}\n  B: {doc_b}")
    print("\nConclusion:", comp.conclusion)


def chat(agente, ruta):
    """Modo conversacional: voy preguntando sobre el mismo documento."""
    agente.cargar(ruta)
    print(f"\nDocumento cargado: {ruta}. Escribe 'salir' para terminar.\n")
    while True:
        pregunta = input("Tu> ").strip()
        if pregunta.lower() in {"salir", "exit", "quit"}:
            break
        print("Agente>", agente.preguntar(pregunta), "\n")


def main():
    parser = argparse.ArgumentParser(description="Agente de documentos academicos en local.")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("resumir").add_argument("archivo")
    sub.add_parser("metadatos").add_argument("archivo")
    cmp = sub.add_parser("comparar")
    cmp.add_argument("archivo_a")
    cmp.add_argument("archivo_b")
    sub.add_parser("chat").add_argument("archivo")

    args = parser.parse_args()
    agente = AgenteAcademico()
    if args.comando == "resumir":
        resumir(agente, args.archivo)
    elif args.comando == "metadatos":
        metadatos(agente, args.archivo)
    elif args.comando == "comparar":
        comparar(agente, args.archivo_a, args.archivo_b)
    elif args.comando == "chat":
        chat(agente, args.archivo)


if __name__ == "__main__":
    main()
