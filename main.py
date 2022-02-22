from tqdm import tqdm
from methods import *
from requests import get
from threading import Thread
from time import sleep
import json


class Autogallery(Thread):
    def __init__(
        self,
        tag: str,
        tags: str,
        path: str,
        max_pages: int = 1,
        start_page: int = 1,
        install_mode="slow",
    ):
        super().__init__()
        self.url = "https://yande.re/post.json?api_version=2&limit=1000"
        self.tag = tag
        self.tags = tags.split(" | ")
        self.path = path
        self.max_pages = max_pages
        self.start_page = start_page
        self.install_mode = install_mode

    def request(self) -> list:
        filtered = []
        print(f'Searching for {", ".join(self.tags)}...')
        self.url += f"&tags={'+'.join(self.tags)}"  # + is used to search for multiple tags. params will only convert it to %2B

        for i in range(self.max_pages):
            try:
                response = get(
                    self.url,
                    params={"tag": self.tag, "page": self.start_page + i},
                )
                res = response.json()
                posts = res.get("posts")
                filtered.extend(posts)
                print(
                    f"..extend {len(posts)} posts. {len(filtered)} total at page {self.start_page + i}."
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
        tag = input("Tag (fixed tag to search for, use _ for spaces): ")
        tags = input(
            'Tags (tags to search for, seperate with |. Example: "tag1 | tag2 | tag3"): '
        )
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
            tag, tags, path, max_pages, start_page, install_mode
        )
        autogal_thread.start()
        while autogal_thread.is_alive():
            sleep(1)


if __name__ == "__main__":
    main()
