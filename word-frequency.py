import requests
import luigi
from bs4 import BeautifulSoup
from collections import Counter
import pickle


class GetTopBooks(luigi.Task):

    def output(self):
        return luigi.LocalTarget('data/book_lists.txt')

    def run(self):
        response = requests.get('http://www.gutenberg.org/browse/scores/top')
        soup = BeautifulSoup(response.content, "html.parser")
        pageHeader = soup.find_all("h2", string="Top 100 EBooks yesterday")[0]
        listTop = pageHeader.find_next_sibling("ol")
        with self.output().open("w") as f:
            for result in listTop.select("li>a"):
                if "/ebooks/" in result["href"]:
                    f.write("http://www.gutenberg.org{link}.txt.utf-8\n"
                        .format(
                        link=result["href"]
                    )
                    )

class DownloadBooks(luigi.Task):
    """
    Download a specified list of books
    """
    FileID = luigi.IntParameter()

    REPLACE_LIST = """.,"';_[]:*-"""

    def requires(self):
        return GetTopBooks()

    def output(self):
        return luigi.LocalTarget("data/downloads/{}.txt".format(self.FileID))

    def run(self):
        with self.input().open("r") as i:
            URL = i.read().splitlines()[self.FileID]

            with self.output().open("w") as outfile:
                book_downloads = requests.get(URL)
                book_text = book_downloads.text

                for char in self.REPLACE_LIST:
                    book_text = book_text.replace(char, " ")

                book_text = book_text.lower()
                outfile.write(book_text)

class CountWords(luigi.Task):
    """
    Count the frequency of the most common words from a file
    """

    FileID = luigi.IntParameter()

    def requires(self):
        return DownloadBooks(FileID=self.FileID)

    def output(self):
        return luigi.LocalTarget(
            "data/counts/count_{}.pickle".format(self.FileID),
            format=luigi.format.Nop
        )

    def run(self):
        with self.input().open("r") as i:
            word_count = Counter(i.read().split())

            with self.output().open("w") as outfile:
                pickle.dump(word_count, outfile)