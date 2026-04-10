# cli.py
import argparse
import os
from mango.evaluation.scripts.evaluate import (
    evaluate_model_dest_finding,
    evaluate_model_route_finding,
)


def main():
    parser = argparse.ArgumentParser(description="CLI for Mango Evaluation")
    parser.add_argument(
        "--mode",
        choices=["rf", "df"],
        help='Evaluation mode: "route_finding" or "dest_finding"',
    )
    parser.add_argument(
        "--rst-dir",
        type=str,
        help="Directory with result files (e.g., output from the model)",
    )
    parser.add_argument(
        "--map-dir", type=str, default="./data", help="Directory with map files"
    )
    parser.add_argument(
        "--output-dir",
        nargs="?",
        default="./output",
        help="Directory to save the evaluation summaries (default: ./output)",
    )

    args = parser.parse_args()
    rst_dir_name = os.path.basename(args.rst_dir)
    args.output_dir = os.path.join(args.output_dir, rst_dir_name)
    if args.mode == "rf":
        evaluate_model_route_finding(args.rst_dir, args.map_dir, args.output_dir)
    elif args.mode == "df":
        evaluate_model_dest_finding(args.rst_dir, args.map_dir, args.output_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
