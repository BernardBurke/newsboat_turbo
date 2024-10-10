import requests
from bs4 import BeautifulSoup

def get_hrefs_from_google(query):
  """
  This function takes a search query as input, sends a request to Google,
  and parses the HTML response to extract the href attributes of the search results.

  Args:
    query: The search query to be used for the Google search.

  Returns:
    A list of strings, where each string is the href attribute of a search result.
  """

  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
  }
  params = {'q': query}

  html = requests.get('https://www.google.com/search', headers=headers, params=params).text
  soup = BeautifulSoup(html, 'lxml')

  hrefs = []
  for result in soup.select('.yuRUbf'):
    href = result.a['href']
    hrefs.append(href)

  return hrefs

# Example usage:
query = "what is python programming language"
hrefs = get_hrefs_from_google(query)

# Print the extracted hrefs
for href in hrefs:
  print(href)