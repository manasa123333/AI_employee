def load_file(file_path):
  import pandas as pd
  if file_path.endswith('.csv'):
    df = pd.read_csv(file_path)
  elif file_path.endswith('.xlsx'):
    df = pd.read_excel(file_path)
  elif file_path.endswith('.json'):
    df = pd.read_json(file_path)
  else:
    raise ValueError("Unsupported file format")
  return df

import pandas as pd

def handle_null_values(df):
    for column in df.columns:
        if df[column].isnull().any():
            if pd.api.types.is_numeric_dtype(df[column]):
                # Replacing null values with the median for numerical columns
                df[column].fillna(df[column].median(), inplace=True)
            elif pd.api.types.is_categorical_dtype(df[column]) or df[column].dtype == object:
                # Replacing null values with the mode for categorical columns
                df[column].fillna(df[column].mode()[0], inplace=True)
    return df

def handle_duplicates(df):
    df.drop_duplicates(inplace=True)
    return df

def clip_zscore(series, z_threshold):
    """
    Clip outliers based on Z-score.
    """
    import numpy as np
    from scipy.stats import zscore
    z_scores = np.abs(zscore(series.dropna()))
    mean, std = series.mean(), series.std()
    lower_bound = mean - z_threshold * std
    upper_bound = mean + z_threshold * std
    return np.clip(series, lower_bound, upper_bound)

def clip_iqr(series, iqr_factor):
    """
    Clip outliers based on IQR.
    """
    import numpy as np
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - (iqr_factor * IQR)
    upper_bound = Q3 + (iqr_factor * IQR)
    return np.clip(series, lower_bound, upper_bound)


def handle_outliers_based_on_distribution(dataFrame, columns=None, z_threshold=3, iqr_factor=1.5):
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  import seaborn as sns
  from scipy.stats import zscore, shapiro, norm , anderson
  from statsmodels.graphics.gofplots import qqplot



  if columns is None:
      columns = dataFrame.select_dtypes(include=['float64', 'int64']).columns

  for column in columns:
      series = dataFrame[column].dropna()
      # Determine dataset size
      n = len(dataFrame[column].dropna())

      # Check if the column is normally distributed
      if n <= 5000:
          # Use Shapiro-Wilk test for small datasets
          stat, p_value = shapiro(dataFrame[column].dropna())
          is_normal = p_value > 0.05
      else:
          # For large datasets, use Anderson-Darling test
          result = anderson(series, dist='norm')
          # Compare the test statistic with critical values for a chosen significance level (e.g., 5%)
          is_normal = result.statistic < result.critical_values[2]  # 2 corresponds to the 5% significance level

      if is_normal:
          print(f"Column '{column}' is normally distributed. Applying Z-score clipping.")
          dataFrame[column] = clip_zscore(dataFrame[column], z_threshold)
      else:
          print(f"Column '{column}' is not normally distributed. Applying IQR clipping.")
          dataFrame[column] = clip_iqr(dataFrame[column], iqr_factor)

  return dataFrame

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def handle_categorical_variables(df):
  """
  Handles categorical variables in a pandas DataFrame by encoding them using the specified method.

  Args:
    df: Input pandas DataFrame.
    encoding_method: Encoding method ('label_encoding', 'one-hot').
    drop_first: Whether to drop the first category in one-hot encoding (default: True).

  Returns:
    Encoded pandas DataFrame.
  """

  categorical_columns = df.select_dtypes(include=['object']).columns
  for column in categorical_columns:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
  return df

def scaled_data(df,target):
  from sklearn.preprocessing import StandardScaler
  scaler = StandardScaler()
  X = scaler.fit_transform(df.drop(target, axis=1))
  y = df[target]
  return X,y

def check_imbalance_and_apply_smote(X, y, threshold=0.6):
  """
  Checks if a dataset is imbalanced based on the class distribution and applies SMOTE if necessary.

  Args:
    X: Input features (pandas DataFrame or numpy array).
    y: Target variable (pandas Series or numpy array).
    threshold: Threshold for considering a dataset imbalanced (default: 0.8).

  Returns:
    Resampled features and target if the dataset is imbalanced, otherwise the original features and target.
  """
  import pandas as pd
  from imblearn.over_sampling import SMOTE

  # Calculate class distribution
  class_distribution = y.value_counts(normalize=True)

  # Check if the dataset is imbalanced
  if max(class_distribution) / min(class_distribution) > threshold:
    print("Dataset is imbalanced.")

    # Apply SMOTE
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    return X_resampled, y_resampled
  else:
    print("Dataset is balanced.")

    return X, y

def data_cleaning_pipeline(filepath,target=None):
  data = load_file(filepath)
  data = handle_null_values(data)
  data = handle_outliers_based_on_distribution(data)
  data = handle_categorical_variables(data)
  data = handle_duplicates(data)
  if target is not None:
    X,y = scaled_data(data,target)
    return X,y
  else:
    return data

def line_plot(df):
  import matplotlib.pyplot as plt
  import seaborn as sns
  # plotting a line plot
  # know the trends in the data
  plt.figure(figsize=(16,6))
  sns.lineplot(data=df)
  plt.title('Line Plot')
  plt.xlabel('X-axis')
  plt.ylabel('Y-axis')
  plt.show()

def scatter_plot(X,y):
  import matplotlib.pyplot as plt
  import seaborn as sns
  plt.figure(figsize = (8,6))
  for column in X.columns:
    plt.scatter(X[column],y)
    plt.xlabel(column)
    plt.ylabel('target')
    plt.title(f'Scatter Plot of {column} vs target')
    plt.legend()
    plt.show()

def histplot(df):
  import matplotlib.pyplot as plt
  import seaborn as sns
  plt.figure(figsize = (8,6))
  for column in df.columns:
    sns.histplot(df[column])
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.title(f'Histogram of {column}')
    plt.legend()
    plt.show()

def linear_regression(X,y):
  from sklearn.model_selection import train_test_split
  from sklearn.metrics import mean_squared_error
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

  from sklearn.linear_model import LinearRegression
  lr = LinearRegression()
  lr.fit(X_train,y_train)
  y_pred = lr.predict(X_test)
  mse = mean_squared_error(y_test, y_pred)
  return mse

def Random_Forest(X,y):
  X,y = check_imbalance_and_apply_smote(X,y)
  from sklearn.model_selection import train_test_split
  from sklearn.metrics import classification_report
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

  from sklearn.ensemble import RandomForestClassifier
  rf = RandomForestClassifier()
  rf.fit(X_train,y_train)
  y_pred = rf.predict(X_test)
  report = classification_report(y_test, y_pred)
  return report

def kmeans_clustering(X, n_clusters=3):
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    return kmeans.labels_, kmeans.inertia_

def analyze_data(df):
    import pandas as pd
    # Calculate basic summary statistics
    summary = df.describe()
    skewness = df.skew()
    kurtosis = df.kurtosis()


    # Create a written summary
    summary_text = []
    summary_text.append(f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
    summary_text.append(f"Summary statistics:\n{summary}")
    summary_text.append(f"Skewness:\n{skewness}")
    summary_text.append(f"Kurtosis:\n{kurtosis}")

    return summary_text

def generate_report(df,X,y = None,type = 'clusterring'):
    import matplotlib.pyplot as plt
    import seaborn as sns
    model_results = {}
    if type == 'regresssion':
      model_results['linear_regression_mse'] = linear_regression(X,y)
    elif type == 'classification':
      model_results['random_forest_report'] = Random_Forest(X,y)
    else:
      model_results['kmeans_labels'], model_results['kmeans_inertia'] = kmeans_clustering(df)
    line_plot(df)
    if y is not None:
      scatter_plot(X,y)
    histplot(df)
    summary_text = analyze_data(df)

    # Print the summary report (you can also return this)
    for line in summary_text:
        print(line)

    return model_results

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def main():
    print("Welcome to the AI Employee!")

    data = None

    while True:
        print("\nChoose an option:")
        print("1. Data cleaning")
        print("2. Analyze Data")
        print("3. Visualize Data")
        print("4. Train Model")
        print("5. Exit")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            file_path = input("Enter the file path: ")
            data = data_cleaning_pipeline(file_path)
            print("Data loaded successfully!")

        elif choice == 2:
            if data is None:
                print("Please load data first.")
                continue
            query = input("Enter your data analysis query.: ")
            # Perform NLP to extract keywords and identify task
            keywords = word_tokenize(query)
            keywords = [word.lower() for word in keywords if word not in stopwords.words('english')]
            print(f"Extracted keywords: {keywords}")

            # Execute the appropriate analysis function based on keywords
            if "summary" in keywords or "statistics" in keywords:
                analyze_data(data)
            elif "correlation" in keywords:
                print("Calculating correlations...")
                correlation_matrix = data.corr()
                print(correlation_matrix)
            else:
                print("Sorry, I didn't understand the analysis request.")

        elif choice == 3:
            if data is None:
                print("Please load data first.")
                continue
            query = input("Enter your visualization query (e.g., 'line plot', 'histogram', 'scatter plot'): ")
            # Perform NLP to extract keywords and identify visualization type
            keywords = word_tokenize(query)
            keywords = [word.lower() for word in keywords if word not in stopwords.words('english')]

            # Execute the appropriate visualization function based on keywords
            if "line" in keywords:
                line_plot(data)
            elif "histogram" in keywords or "hist" in keywords:
                histplot(data)
            elif "scatter" in keywords:
                if target is None:
                    print("Please provide target variable to plot scatter plot.")
                else:
                    scatter_plot(data.drop(target, axis=1), data[target])
            else:
                print("Sorry, I didn't understand the visualization request.")

        elif choice == 4:
            if data is None:
                print("Please load data first.")
                continue

            type_of_model = input("Enter model type (e.g., 'classification', 'regression', 'clustering'): ").lower()
            target = None # Define target here to make it accessible in the else block
            if type_of_model == 'classification':
                target = input("Enter the target variable for classification: ")
            elif type_of_model == 'regression':
                target = input("Enter the target variable for regression: ")

            if target is not None: # Add a check to ensure target is assigned
                X, y = scaled_data(data, target)

                if type_of_model == 'regression':
                    mse = linear_regression(X, y)
                    print(f"Mean Squared Error of the model: {mse}")
                elif type_of_model == 'classification':
                    report = Random_Forest(X, y)
                    print(f"Classification Report:\n{report}")
                else:
                    print("Unsupported model type. Please choose 'classification' or 'regression'.")
            elif type_of_model == 'clustering': # Handle clustering separately as it doesn't need a target
                X = scaled_data(data) # Assuming scaled_data can handle no target
                labels, inertia = kmeans_clustering(X)
                print(f"K-Means clustering completed with inertia: {inertia}")
            else:
                print("Unsupported model type. Please choose 'classification', 'regression', or 'clustering'.")

        elif choice == 6:
            print("Exiting the application.")
            break

        else:
            print("Invalid choice. Please choose a valid option.")


if __name__ == "__main__":
    main()

import unittest
import pandas as pd

class TestDataCleaning(unittest.TestCase):

    def test_datacleaning(self):
      cleaned_dataset = data_cleaning_pipeline('/content/olympics2024.csv')

      self.assertIsNotNone(cleaned_dataset,"The cleaned dataset should not be None.")
      self.assertIsInstance(cleaned_dataset, pd.DataFrame,"The cleaned dataset should be a pandas DataFrame.")
      self.assertFalse(cleaned_dataset.isnull().values.any(), "The dataset still contains missing values.")
      self.assertFalse(cleaned_dataset.duplicated().any(), "The dataset still contains duplicate rows.")

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)

class TestDataAnalyze(unittest.TestCase):

    def test_AnalyzeData(self):
      cleaned_dataset = data_cleaning_pipeline('/content/olympics2024.csv')
      analyze = analyze_data(cleaned_dataset)
      self.assertIsNotNone(cleaned_dataset,"The cleaned dataset should not be None.")
      self.assertIsInstance(cleaned_dataset, pd.DataFrame,"The cleaned dataset should be a pandas DataFrame.")
      self.assertIsNotNone(analyze,"The summary should not be None.")


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)

class TestDataVisualize(unittest.TestCase):

    def test_VisualizeData(self):
        # Clean the dataset
        cleaned_dataset = data_cleaning_pipeline('/content/olympics2024.csv')

        # Ensure the cleaned dataset is valid
        self.assertIsNotNone(cleaned_dataset, "The cleaned dataset should not be None.")
        self.assertIsInstance(cleaned_dataset, pd.DataFrame, "The cleaned dataset should be a pandas DataFrame.")

        # Check if line_plot executes without errors
        try:
            line_plot(cleaned_dataset)
        except Exception as e:
            self.fail(f"line_plot raised an exception: {e}")

        # Check if histplot executes without errors
        try:
            histplot(cleaned_dataset)
        except Exception as e:
            self.fail(f"histplot raised an exception: {e}")

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)

cleaned_dataset = data_cleaning_pipeline('/content/olympics2024.csv')
print(cleaned_dataset.columns)

import unittest
import pandas as pd


class TestTrainModel(unittest.TestCase):

    def test_TrainModel(self):
        # Clean the dataset
        cleaned_dataset = data_cleaning_pipeline('/content/olympics2024.csv')
        print(cleaned_dataset.columns)

        target_regression = 'Total'  # Predict total number of medals


        Rx,Ry = data_cleaning_pipeline('/content/olympics2024.csv',target_regression)
        Cx,Cy = data_cleaning_pipeline('/content/Iris.csv','Species')

        # Ensure the cleaned dataset is valid
        self.assertIsNotNone(cleaned_dataset, "The cleaned dataset should not be None.")
        self.assertIsInstance(cleaned_dataset, pd.DataFrame, "The cleaned dataset should be a pandas DataFrame.")
        regression = linear_regression(Rx,Ry)
        classification = Random_Forest(Cx,Cy)
        clustering = kmeans_clustering(cleaned_dataset)
        self.assertIsNotNone(regression,"The regression model should not be None.")
        self.assertIsNotNone(classification,"The classification model should not be None.")
        self.assertIsNotNone(clustering,"The clustering model should not be None.")


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)

