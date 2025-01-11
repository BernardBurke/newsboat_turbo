import requests
import os
from datetime import datetime

def download_imdb_datasets(save_dir="imdb_data"):
  """
  Downloads the daily IMDb datasets and saves them locally.

  Args:
    save_dir: The directory where the datasets will be saved.
  """

  # Create the save directory if it doesn't exist
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)

  # IMDb dataset URLs
  dataset_urls = [
      "https://datasets.imdbws.com/title.akas.tsv.gz",
      "https://datasets.imdbws.com/title.basics.tsv.gz",
      "https://datasets.imdbws.com/title.crew.tsv.gz",
      "https://datasets.imdbws.com/title.episode.tsv.gz",
      "https://datasets.imdbws.com/title.principals.tsv.gz",
      "https://datasets.imdbws.com/title.ratings.tsv.gz",
      "https://datasets.imdbws.com/name.basics.tsv.gz"
  ]

  # Download each dataset
  for url in dataset_urls:
    filename = os.path.join(save_dir, url.split("/")[-1])
    print(f"Downloading {filename}...")

    try:
      response = requests.get(url, stream=True)
      response.raise_for_status()  # Raise an exception for bad status codes

      with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
          f.write(chunk)

      print(f"Downloaded {filename}")
    except requests.exceptions.RequestException as e:
      print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
  # Get the current date for directory naming
  today = datetime.today().strftime('%Y-%m-%d')
  save_directory = f"imdb_data_{today}"

  download_imdb_datasets(save_directory)
