import requests
import os
import gzip
import sqlite3
from datetime import datetime

def download_imdb_datasets(save_dir="imdb_data"):
    """
    Downloads, unzips, and loads the daily IMDb datasets into a SQLite database.

    Args:
        save_dir: The directory where the datasets will be saved.
    """

    # Create the save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # IMDb dataset URLs
    dataset_urls = {
        "title.akas.tsv.gz": "akas",
        "title.basics.tsv.gz": "basics",
        "title.crew.tsv.gz": "crew",
        "title.episode.tsv.gz": "episode",
        "title.principals.tsv.gz": "principals",
        "title.ratings.tsv.gz": "ratings",
        "name.basics.tsv.gz": "names"
    }

    # Database setup
    db_path = os.path.join(save_dir, "imdb.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Download and process each dataset
    for url, table_name in dataset_urls.items():
        filename = os.path.join(save_dir, url)
        print(f"Downloading {filename}...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded {filename}")

            # Unzip the file
            unzipped_filename = filename[:-3]  # Remove .gz extension
            with gzip.open(filename, 'rt', encoding='utf-8') as gz_file:
                with open(unzipped_filename, 'wt', encoding='utf-8') as f:
                    f.write(gz_file.read())

            print(f"Unzipped {filename}")

            # Load data into SQLite
            with open(unzipped_filename, 'r', encoding='utf-8') as f:
                header = f.readline().strip().split('\t')
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {', '.join([f'"{col}" TEXT' for col in header])}
                    );
                """
                cursor.execute(create_table_sql)

                for line in f:
                    values = line.strip().split('\t')
                    insert_sql = f"""
                        INSERT INTO {table_name} ({', '.join([f'"{col}"' for col in header])})
                        VALUES ({', '.join(['?' for _ in header])});
                    """
                    cursor.execute(insert_sql, values)

            conn.commit()
            print(f"Loaded {unzipped_filename} into database")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    conn.close()
    print("Finished processing all datasets.")

if __name__ == "__main__":
    # Get the current date for directory naming
    today = datetime.today().strftime('%Y-%m-%d')
    save_directory = f"imdb_data_{today}"

    download_imdb_datasets(save_directory)
