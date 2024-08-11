
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
import pickle

text_preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(), 'transformed_text'),
        ('link', TfidfVectorizer(), 'transformed_link')
    ],
    sparse_threshold=0  # Ensure the output is a sparse matrix
)

# Define the full preprocessing and modeling pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', ColumnTransformer(
        transformers=[
            ('text', text_preprocessor, [
             'transformed_text', 'transformed_link'])
        ]
    )),
    ('classifier', RandomForestClassifier())
])

with open('label_encoder.pkl', 'rb') as file:
    label_encoder = pickle.load(file)

# Load the model from a file
with open('pipeline.pkl', 'rb') as f:
    model = pickle.load(f)


def predictor(single_row):

    single_row_transformed = pipeline.named_steps['preprocessor'].transform(
        single_row)
    res = pipeline.named_steps['classifier'].predict(single_row_transformed)
    res = label_encoder.inverse_transform(res)[0]
    return res
