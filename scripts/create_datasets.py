import os
import json
import requests
from bs4 import BeautifulSoup

class LyricDatasetCreator:
    def __init__(self):
        data = open("ia/nlp/param/data.json")
        self.variables = json.load(data)
        self.url = self.variables["url"]
        self.dataset_dir = self.variables["dataset_dir"]

    def create_lyric_dataset(self, name):
        url = requests.get(f"{self.url}{name.replace(' ', '-').lower()}")
        soup = BeautifulSoup(url.content, features="lxml")

        try:
            songs = soup.find_all("a", class_="song-name")
            if len(songs) == 0:
                print("Sorry, nothing was found!")
                return

            artist_dir = f"{self.dataset_dir}{name.replace(' ', '_').lower()}"
            if not os.path.exists(artist_dir):
                os.makedirs(artist_dir)
            count = 0
            for song in songs:
                count = count + 1
                song_title = song.get_text().strip()
                song_url = f"{self.url}{name.replace(' ', '-').lower()}/{song_title.replace(' ', '-').lower()}"
                song_request = requests.get(song_url)
                song_soup = BeautifulSoup(song_request.content, features="lxml")

                more_pages = song_soup.find_all("li", class_="pager-item")
                if len(more_pages) > 0:
                    page_urls = [song_url]
                    for page in more_pages:
                        page_url = f"{self.url}{page.find('a')['href']}"
                        page_urls.append(page_url)

                    result = ""
                    for page_url in page_urls:
                        page_request = requests.get(page_url)
                        page_soup = BeautifulSoup(page_request.content, features="lxml")
                        lyrics = page_soup.find_all("div", class_="cnt-letra")
                        if len(lyrics) > 0:
                            for i in lyrics:
                                result += i.get_text("<p>").replace("<p>", "\n")
                else:
                    lyrics = song_soup.find_all("div", class_="cnt-letra")
                    if len(lyrics) > 0:
                        for i in lyrics:
                            result = i.get_text("<p>").replace("<p>", "\n")

                file_path = os.path.join(artist_dir, f"{song_title.replace(' ', '_').lower()}.txt")
                with open(file_path, "a", encoding='UTF-8') as output:
                    output.write(f"{name.replace('-', ' ').upper()} - {song_title.replace('-', ' ').upper()}\n\n{result.strip()}\n\n")
                print(f"Lyric '{song_title}' was saved!")
            

        except:
            print(f"Total of files: {count}")
            print("Finished")

    def main(self):
        name = input("Type a singer or band name: ")
        self.create_lyric_dataset(name)

