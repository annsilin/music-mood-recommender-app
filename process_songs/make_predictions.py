import pandas as pd
import joblib
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_FILE = os.path.join(current_directory, 'classifier.pkl')
LABEL_ENCODER_FILE = os.path.join(current_directory, 'label_encoder.pkl')


def calculate_tonality(row):
    """
    Calculates the musical tonality based on a row's 'key' and 'mode' values.

    Args:
        row (pandas.Series): A row from a DataFrame containing 'key' and 'mode' columns.

    Returns:
        int: The calculated musical tonality value.
    """
    key = row['key']
    mode = row['mode']
    if mode == 1:  # major mode
        tonality = key * 2  # Major represented by even numbers
    else:  # minor mode
        tonality = key * 2 + 1  # Minor represented by odd numbers
    return tonality


def add_tonality_column(df):
    """
    Adds a new 'tonality' column to a DataFrame by applying the 'calculate_tonality' function to each row.

    Args:
        df (pandas.DataFrame): The DataFrame containing 'key' and 'mode' columns.

    Returns:
        pandas.DataFrame: The DataFrame with the added 'tonality' column.
    """
    df['tonality'] = df.apply(calculate_tonality, axis=1)
    return df


def check_columns_exist(df, required_columns):
    """
    Check if all required columns exist in the DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame with necessary features for predictions.
        required_columns (list of strings): Required column names.

    Returns:
        boolean: True if all required columns exist, False otherwise.
    """
    return all(col in df.columns for col in required_columns)


def make_predictions(dataset_path, output_path):
    """
    Applies a pre-trained classifier to predict probabilities and saves the results to a CSV file.

    Args:
        dataset_path (str): Path to the dataset CSV file.
        output_path (str): Path to save the output CSV file.

    Returns:
    None
    """
    df = pd.read_csv(dataset_path)

    feature_columns = ['acousticness', 'danceability', 'energy', 'key', 'mode', 'loudness',
                       'speechiness', 'instrumentalness', 'liveness', 'valence',
                       'tempo', 'duration_ms', 'time_signature']

    if not check_columns_exist(df, feature_columns):
        raise Exception('Required columns for mood predictions are missing in the CSV file.')

    df = df.dropna(subset=feature_columns)

    df = df.astype({'time_signature': 'int', 'key': 'int', 'mode': 'int'})
    df = add_tonality_column(df)
    df = df.astype({"tonality": "category", "time_signature": "category"})

    new_feature_columns = ['acousticness', 'danceability', 'energy', 'tonality', 'loudness',
                           'speechiness', 'instrumentalness', 'liveness', 'valence',
                           'tempo', 'duration_ms', 'time_signature']

    features_df = df[new_feature_columns]

    model = joblib.load(CLASSIFIER_FILE)
    label_encoder = joblib.load(LABEL_ENCODER_FILE)

    encoded_predictions = model.predict_proba(features_df)
    class_labels = label_encoder.classes_
    decoded_predictions_df = pd.DataFrame(encoded_predictions, columns=class_labels)
    result_df = pd.concat([df, decoded_predictions_df], axis=1)

    result_df.to_csv(output_path, index=False)
