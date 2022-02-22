from tqdm import tqdm
from methods import *
from requests import get
from threading import Thread
from time import sleep
import json


class Autogallery(Thread):
    def __init__(
        self,
        keywords: str,
        tag: str,
        path: str,
        max_pages: int = 1,
        start_page: int = 1,
        install_mode="slow",
    ):
        super().__init__()
        self.url = "https://yande.re/post.json?api_version=2&limit=1000"
        self.keywords = keywords.split(" | ")
        self.tag = tag
        self.path = path
        self.max_pages = max_pages
        self.start_page = start_page
        self.install_mode = install_mode

    def request(self) -> list:
        filtered = []
        print(f'Searching for {", ".join(self.keywords)}...')

        for i in range(self.max_pages):
            try:
                response = get(
                    self.url, params={"tags": self.tag, "page": self.start_page + i}
                )
                res = response.json()
                _filteredByTag = list(
                    filter(
                        lambda post: self.tag in post.get("tags").lower(),
                        res.get("posts"),
                    )
                )
                _filteredByKeywords = list(
                    filter(
                        lambda post: [
                            keyword
                            for keyword in self.keywords
                            if keyword.lower() in post.get("tags").lower()
                        ]
                        != [],
                        _filteredByTag,
                    )
                )
                filtered.extend(_filteredByKeywords)
                print(
                    f"..extend {len(_filteredByKeywords)} posts. {len(filtered)} total at page {self.start_page + i}."
                )
            except json.JSONDecodeError:
                if "can't go beyond requested page" in response.text.lower():
                    print("!!! Maximum page reached !!!")
                    return filtered
                elif "rate" in response.text.lower():
                    print("!!! Rate limit reached !!!\nSleeping for 5 minutes...")
                    sleep(5)
                    continue

        return filtered

    def run(self):
        posts = self.request()

        if not posts:
            return print("No posts found.")

        print(f"Found {len(posts)} posts. Using {self.install_mode} mode to install.")

        if self.install_mode == "slow":
            for i in tqdm(range(len(posts)), desc="Downloading"):
                for post in posts:
                    saveImageFromUrl(
                        url=post.get("file_url"),
                        path=f"{self.path}/{post.get('id')}.{post.get('file_ext')}",
                    )

        elif self.install_mode == "fast":
            threads = [
                Thread(
                    target=saveImageFromUrl,
                    kwargs={
                        "url": post.get("file_url"),
                        "path": f"{self.path}/{post.get('id')}.{post.get('file_ext')}",
                    },
                )
                for post in posts
            ]

            for thread in threads:
                thread.start()

            for i in tqdm(range(len(threads)), desc="Downloading"):
                while threads[i].is_alive():
                    sleep(0.1)

        else:
            print("!!! Invalid install mode !!!")

        print("Done.")


def main():
    while 1:
        keywords = input(
            '\nKeywords (words that must be included in tags, seperate with |. Example: "some | text" ): '
        )
        tag = input("Tag (actual tag to search for): ")
        path = input("Save path (path the images get saved at): ")
        max_pages = int(input("Max pages (max number of pages to search): "))
        start_page = int(input("Start page (page to start at): "))
        install_mode = input(
            """Install mode (
                slow -> safe downloads
                fast -> might break downloads
            \r): """
        )
        autogal_thread = Autogallery(
            keywords, tag, path, max_pages, start_page, install_mode
        )
        autogal_thread.start()
        while autogal_thread.is_alive():
            sleep(1)


if __name__ == "__main__":
    main()
