

import pandas as pd

# from common import headers

from solution.pipline import data_pipeline
from solution.preprocessor import dataFrameCreator
from solution.prediction_pipeline import predictor


def main(url):
    text = data_pipeline(url)
    df = dataFrameCreator(url, text)
    res = predictor(df)
    print(res)


if __name__ == '__main__':
    url = 'https://lfillumination.com/files/specsheets/EF408B-Light-Unit.pdf'
    main(url)
