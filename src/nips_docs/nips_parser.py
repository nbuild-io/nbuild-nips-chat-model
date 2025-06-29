import requests
from bs4 import BeautifulSoup
import markdown
import json
import csv
import re
from typing import List, Tuple, Optional, Set
from tqdm import tqdm


class NIPSParser:
    """
    A scraper to fetch markdown NIPS documents from URLs, parse them,
    extract headings and paragraphs, and generate Q&A pairs suitable for training language models.

    Attributes:
        urls (List[str]): List of URLs pointing to Markdown documents.
        min_heading_length (int): Minimum length of heading to consider for generating Q&A pairs.
        all_qa_pairs (List[dict]): Collected list of generated Q&A pairs.
        seen_questions (Set[str]): Set of already seen questions (for deduplication).
        skipped_count (int): Number of skipped empty answers.
    """

    def __init__(self, urls: List[str], min_heading_length: int = 3) -> None:
        """
        Initializes the NIPSParser with a list of URLs.

        Args:
            urls (List[str]): List of URLs pointing to Markdown documents.
            min_heading_length (int): Minimum length of heading to consider for generating Q&A pairs.
        """
        self.urls = urls
        self.min_heading_length = min_heading_length
        self.all_qa_pairs: List[dict] = []
        self.seen_questions: Set[str] = set()
        self.skipped_count: int = 0

    def fetch_and_parse(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetches a Markdown document from the given URL, converts it to HTML,
        and parses it into a BeautifulSoup object.

        Args:
            url (str): The URL of the Markdown document.

        Returns:
            Optional[BeautifulSoup]: Parsed HTML content as a BeautifulSoup object,
            or None if the request failed.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            md_content = response.text
            html_content = markdown.markdown(md_content)
            soup = BeautifulSoup(html_content, "html.parser")
            return soup
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_headings_and_content(self, soup: BeautifulSoup) -> Tuple[List[str], List[str]]:
        """
        Extracts headings and associated content (paragraphs, lists, code blocks) from HTML.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            Tuple[List[str], List[str]]: A tuple of headings and their corresponding content blocks.
        """
        headings = []
        contents = []

        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = header.get_text(strip=True)
            if len(heading_text) < self.min_heading_length:
                continue

            content_blocks = []

            for sibling in header.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break

                if sibling.name == 'p':
                    content_blocks.append(sibling.get_text(strip=True))

                if sibling.name in ['ul', 'ol']:
                    list_items = [
                        f"- {li.get_text(strip=True)}" for li in sibling.find_all('li')
                    ]
                    content_blocks.append("\n".join(list_items))

                if sibling.name == 'pre':
                    code_block = sibling.get_text()
                    content_blocks.append(f"```\n{code_block.strip()}\n```")

                elif sibling.name == 'code' and not sibling.find_parent('pre'):
                    code_inline = sibling.get_text(strip=True)
                    content_blocks.append(f"`{code_inline}`")

            raw_answer = "\n\n".join(content_blocks)
            cleaned_answer = self.clean_answer_text(raw_answer)

            if cleaned_answer.strip():
                headings.append(heading_text)
                contents.append(cleaned_answer)
            else:
                self.skipped_count += 1

        return headings, contents

    @staticmethod
    def clean_answer_text(text: str) -> str:
        """
        Cleans the extracted answer text.

        - Preserves line breaks for code blocks and lists.
        - Removes excessive whitespace.
        - Collapses multiple blank lines into one.

        Args:
            text (str): Raw-extracted text.

        Returns:
            str: Cleaned text.
        """
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = "\n".join(line.strip() for line in text.splitlines())
        return text.strip()

    def generate_qa_pairs(self, headings: List[str], paragraphs: List[str]) -> List[dict]:
        """
        Generates question-answer pairs using the extracted headings and paragraphs.

        Args:
            headings (List[str]): List of headings to generate questions from.
            paragraphs (List[str]): List of paragraphs to serve as answers.

        Returns:
            List[dict]: A list of dictionaries, each containing a 'question' and an 'answer' key.
        """
        qa_pairs = []
        for i, heading in enumerate(headings):
            question = f"What does {heading} mean?"

            if question in self.seen_questions:
                continue

            answer = paragraphs[i] if i < len(paragraphs) else "No content available."
            qa_pairs.append({"question": question, "answer": answer})
            self.seen_questions.add(question)

        return qa_pairs

    def scrape(self) -> None:
        """
        Main method to loop through all URLs and collect Q&A pairs.
        Displays progress using tqdm progress bar.
        """
        print("Scraping NIPS documents...")
        for url in tqdm(self.urls, desc="Processing URLs"):
            soup = self.fetch_and_parse(url)
            if soup:
                headings, paragraphs = self.extract_headings_and_content(soup)
                qa_pairs = self.generate_qa_pairs(headings, paragraphs)
                self.all_qa_pairs.extend(qa_pairs)

        print(f"\nScraping complete. Skipped {self.skipped_count} empty or invalid sections.")

    def save_to_jsonl(self, output_file: str) -> None:
        """
        Saves the collected Q&A pairs to a JSONL (JSON Lines) file.

        Args:
            output_file (str): Path to the output JSONL file.
        """
        with open(output_file, "w", encoding="utf-8") as outfile:
            for pair in self.all_qa_pairs:
                json.dump(pair, outfile, ensure_ascii=False)
                outfile.write("\n")
        print(f"Q&A dataset saved as '{output_file}'.")

    def save_to_csv(self, output_file: str) -> None:
        """
        Saves the collected Q&A pairs to a CSV file.

        Args:
            output_file (str): Path to the output CSV file.
        """
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["question", "answer"])
            writer.writeheader()
            for pair in self.all_qa_pairs:
                writer.writerow(pair)
        print(f"Q&A dataset saved as '{output_file}'.")
