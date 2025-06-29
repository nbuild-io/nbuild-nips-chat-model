import argparse
import os
import sys
import yaml
from typing import List

from nips_docs import NIPS_URLS
from nips_parser import NIPSParser
from nips_github_private_repo import NIPSGitHubFetcher

DEFAULT_CONFIG_PATH = "data/axolotl_config.yaml"


def get_nips_urls(private: bool = False) -> List[str]:
    """
    Get the list of NIPS document URLs.

    Args:
        private (bool): If True, fetch URLs from a private GitHub repository;
                        if False, use public URLs.

    Returns:
        List[str]: List of URLs.
    """
    if private:
        fetcher = NIPSGitHubFetcher()
        return fetcher.fetch_nips_urls()
    else:
        return NIPS_URLS


def run_scrape_command(args: argparse.Namespace) -> None:
    """
    Execute the scraping process using configuration from the YAML file.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    with open(args.config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    scraping_config = config.get("scraping", {})
    min_heading_length = scraping_config.get("min_heading_length", 3)
    output_config = scraping_config.get("output", {})

    jsonl_output_path = output_config.get("jsonl", "nips_dataset.jsonl")
    csv_output_path = output_config.get("csv", "nips_dataset.csv")

    print(f"Using min_heading_length={min_heading_length}")
    print(f"Saving JSONL output to: {jsonl_output_path}")
    print(f"Saving CSV output to: {csv_output_path}")

    nips_urls = get_nips_urls(private=args.private)
    nips_parser = NIPSParser(nips_urls, min_heading_length=min_heading_length)

    nips_parser.scrape()
    nips_parser.save_to_jsonl(jsonl_output_path)
    nips_parser.save_to_csv(csv_output_path)


def main() -> None:
    """
    Main entry point for the CLI tool.

    Supports the flags:
      --scrape    : Scrape NIPS documents and generate Q&A pairs.

    Use a YAML config file (default: data/axolotl_config.yaml) for parameters.
    """
    parser = argparse.ArgumentParser(prog="NIPS CLI", description="NIPS Scrape & Fine-tune CLI")
    parser.add_argument(
        "--config-path",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to config YAML file (default: {DEFAULT_CONFIG_PATH})",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scrape",
        action="store_true",
        help="Scrape NIPS docs and generate Q&A pairs."
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Use private GitHub repo for URLs (only relevant with --scrape).",
    )
    args = parser.parse_args()
    if args.scrape:
        run_scrape_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
