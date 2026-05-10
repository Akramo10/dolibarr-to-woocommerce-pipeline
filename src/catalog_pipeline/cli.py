from __future__ import annotations

import argparse

from .pipeline import process_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare Dolibarr product exports for WooCommerce.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process = subparsers.add_parser("process", help="Clean and export products.")
    process.add_argument("--input", required=True, help="Input CSV or Excel file.")
    process.add_argument("--output-dir", default="exports", help="Output directory.")

    args = parser.parse_args()
    if args.command == "process":
        result = process_file(args.input, args.output_dir)
        print(f"Products ready: {len(result.ready)}")
        print(f"Duplicate rows: {len(result.duplicates)}")
        print(f"Missing price rows: {len(result.missing_price)}")
        print(f"Output directory: {result.output_dir}")


if __name__ == "__main__":
    main()
