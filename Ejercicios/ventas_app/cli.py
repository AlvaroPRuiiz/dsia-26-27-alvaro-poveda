import argparse
from pathlib import Path

from ventas_app.loader import load
from ventas_app.validator import validar_ventas


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()

    frame = load(args.input)
    validos, errores = validar_ventas(frame)

    validos.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()