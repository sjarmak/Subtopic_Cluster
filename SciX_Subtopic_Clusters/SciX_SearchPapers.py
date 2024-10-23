import json
import requests
import os
import time
import argparse

ADS_API_TOKEN = 'YOUR-API-KEY'  # Replace with your actual ADS API token

def fetch_papers_from_ads(query, max_results=100):
    headers = {
        'Authorization': f'Bearer {ADS_API_TOKEN}'
    }
    fields = "title,abstract,year"
    rows = 100  # Adjust based on the API's max limit
    start = 0

    papers = []

    while len(papers) < max_results:
        url = f"https://api.adsabs.harvard.edu/v1/search/query?q={query}&fl={fields}&start={start}&rows={rows}&sort=relevance"
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'response' not in data or 'docs' not in data['response']:
            print(data)  # Print any error messages
            break

        papers.extend(data['response']['docs'])
        start += rows

        if len(papers) >= max_results or len(data['response']['docs']) < rows:
            break

    return papers[:max_results]


def save_to_jsonl(papers, dir_name, query):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(os.path.join(dir_name, f'{query}.jsonl'), 'w') as file:
        for paper in papers:
            json.dump(paper, file)
            file.write('\n')


def search_papers_in_ads(query, output_dir, max_results=1000):
    papers = fetch_papers_from_ads(query, max_results)
    save_to_jsonl(papers, os.path.join(f"{output_dir}/{query}"), query)
    print(f"Total {len(papers)} papers")
    return papers


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', dest='query', type=str, help='query to search')
    parser.add_argument('--output_dir', dest='output_dir', type=str, help='output directory to save the papers')
    parser.add_argument('--max_results', dest='max_results', default=1000, type=int, help='maximum number of papers to fetch')
    args = parser.parse_args()

    search_papers_in_ads(args.query, args.output_dir, args.max_results)