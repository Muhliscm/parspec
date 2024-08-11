import nltk
from nltk.stem.porter import PorterStemmer
import string
from nltk.corpus import stopwords
import pandas as pd


ps = PorterStemmer()


def transformation(text):
    # lower text
    text = text.lower()
    # convert into words
    text = nltk.word_tokenize(text)

    # removing special characters
    y = []
    for str_ in text:
        if str_.isalnum():
            y.append(str_)

    text = y.copy()
    y.clear()

    # removing stop words and punctuation
    for str_ in text:
        if str_ not in stopwords.words('english') and str_ not in string.punctuation:
            y.append(str_)

    text = y.copy()
    y.clear()

    # stemming
    for str_ in text:
        y.append(ps.stem(str_))

    return " ".join(y)


def link_preprocessor(link):
    link = " ".join([str_.strip() for str_ in link.split(
        '/') if str_.strip() and ("http" not in str_ and 'www' not in str_)])

    link = transformation(link)

    link_len = len(nltk.word_tokenize(link))

    return link, link_len


def text_processor(text):
    text_len = len(nltk.word_tokenize(text))
    text = transformation(text)
    return text, text_len


def dataFrameCreator(url, text):
    link, link_len = link_preprocessor(url)
    text, text_len = text_processor(text)

    single_row = pd.DataFrame({
        'num_link_words': [link_len],
        'num_content_words': [text_len],
        'transformed_text': [text],  # Assuming text is preprocessed
        'transformed_link': [link]
    })

    return single_row
