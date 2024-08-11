import requests
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from io import BytesIO
import unicodedata
from lxml import html
from .utils import check_status, check_content_type
import time
from requests.exceptions import RequestException


# not_scrapped_urls = []
MAX_RETRIES = 3
RETRY_DELAY = 2

headers = {
    'authority': 'www.mcgillmicrowave.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}


def unicode_converter(_str):
    return unicodedata.normalize('NFKD', _str).encode('ascii', errors='replace').decode().replace('?', " ")


class PdfPipeline:
    def __init__(self, response) -> None:
        self.response = response

    def extract_text_from_pdf(self):
        pdf_stream = BytesIO(self.response.content)
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            image = Image.open(BytesIO(pix.tobytes()))
            text += PdfPipeline.extract_text_from_image(image) + "\n"

        text = text.replace("\t", " ").replace("\n", " ")
        text = unicode_converter(text)
        text = text.replace("  ", " ")
        return text

    @staticmethod
    def extract_text_from_image(image):
        return pytesseract.image_to_string(image)


class HtmlPipeline:
    def __init__(self, response) -> None:
        self.response = response

    def parser(self):
        try:
            tree = html.fromstring(self.response.content)
        except Exception as ex:
            print(f"Exception: {ex} occurred for url:{self.response.url}")
            # response.raise_for_status()
            # tree = ""

        text = ""
        if tree:
            for unwanted_element in tree.xpath('//script | //style'):
                unwanted_element.getparent().remove(unwanted_element)

            text = " ".join([str_.strip() for str_ in tree.xpath(
                '//body//text()') if str_.strip()])
            text = text.replace("\t", " ").replace('\n', " ")
            text = unicode_converter(text)
            text = text.replace('  ', " ")
        return text

    def get_text(self):
        return self.parser()


def data_pipeline(url):
    headers['authority'] = url
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if check_status(response):
                content_type = check_content_type(response)
                if content_type == 'PDF':
                    pipeline = PdfPipeline(response)
                    text = pipeline.extract_text_from_pdf()
                    return text
                elif content_type == "HTML":
                    pipeline = HtmlPipeline(response)
                    text = pipeline.get_text()
                    return text
                else:
                    return response.content
            else:
                return f"Failed to scrape {url}"

        except (RequestException, Exception) as e:
            print(f"Error scraping {url}: {e}")
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Retrying {url} ({retries}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                print(f"Failed to scrape {url} after {MAX_RETRIES} retries.")
