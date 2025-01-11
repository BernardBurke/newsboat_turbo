import requests

def imdb_search(query):
  """
  Searches IMDb for movies and displays the results.

  Args:
    query: The search query (movie title, actor name, etc.).
  """

  url = f"https://imdb-api.com/en/API/SearchMovie/k_12345678/{query}"  # Replace k_12345678 with your actual API key

  response = requests.get(url)
  data = response.json()

  if data['results']:
    for result in data['results']:
      print(f"{result['title']} ({result['description']})")
      print(f"  IMDb ID: {result'id']}")
      print(f"  Image: {result['image']}")
      print("-" * 20)
  else:
    print("No results found.")

if __name__ == "__main__":
  query = input("Enter your IMDb search query: ")
  imdb_search(query)
