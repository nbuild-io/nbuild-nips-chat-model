import requests
from typing import List
import base64
import github_config


class NIPSGitHubFetcher:
    """
    Fetches the NIPS_URLS list from a private GitHub repository.
    """

    def __init__(self) -> None:
        """
        Initializes the GitHub fetcher with credentials and repo details from github_config.py.
        """
        self.username = github_config.GITHUB_USERNAME
        self.token = github_config.GITHUB_TOKEN
        self.repo_owner = github_config.REPO_OWNER
        self.repo_name = github_config.REPO_NAME
        self.urls_file_path = "nips_docs.py"

    def fetch_urls_file_content(self) -> str:
        """
        Fetches the raw content of the nips_docs.py file from the private GitHub repo.

        Returns:
            str: The decoded content of the file.
        """
        api_url = (
            f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.urls_file_path}"
        )
        response = requests.get(api_url, auth=(self.username, self.token))

        if response.status_code == 200:
            content_json = response.json()
            encoded_content = content_json["content"]
            decoded_bytes = base64.b64decode(encoded_content)
            return decoded_bytes.decode("utf-8")
        else:
            raise Exception(
                f"Failed to fetch {self.urls_file_path} from GitHub: {response.status_code} {response.text}"
            )

    def parse_nips_urls(self, file_content: str) -> List[str]:
        """
        Parses the NIPS_URLS list from the fetched Python file content.

        Args:
            file_content (str): The raw content of the nips_docs.py file.

        Returns:
            List[str]: List of URLs extracted from the file.
        """
        urls = []
        inside_urls_list = False

        for line in file_content.splitlines():
            line = line.strip()
            if line.startswith("NIPS_URLS") and "=" in line:
                inside_urls_list = True
                continue

            if inside_urls_list:
                if line.startswith("]"):
                    break

                if line.startswith('"') or line.startswith("'"):
                    url = line.strip(",").strip("'").strip('"')
                    urls.append(url)

        if not urls:
            raise Exception("No URLs found in NIPS_URLS list!")

        return urls

    def fetch_nips_urls(self) -> List[str]:
        """
        High-level method to fetch and parse the NIPS_URLS list.

        Returns:
            List[str]: List of NIPS document URLs.
        """
        print("Fetching NIPS_URLS from GitHub private repo...")
        file_content = self.fetch_urls_file_content()
        urls = self.parse_nips_urls(file_content)
        print(f"Fetched {len(urls)} URLs.")
        return urls
