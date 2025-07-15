
from bs4 import BeautifulSoup
class HtmlHandler:

    def parse_ngrok_front_page(self, page):
        html = BeautifulSoup(page, "html.parser")
