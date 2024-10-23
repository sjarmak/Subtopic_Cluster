import json
import os
import pickle
# from openai import OpenAI
import openai
from openai import OpenAI
import streamlit as st
import argparse
from SciX_Navigator_utils import load_papers
import numpy as np

openai.api_key = 'YOUR-API-KEY'

def is_title_already_in_data(doc, data):
    title = doc.get('title')
    
    # Convert title from list to string if needed
    if isinstance(title, list):
        title = " ".join(title)
    
    if not isinstance(title, str):
        print(f"Skipping document with invalid or missing title: {title}")
        return False

    title = title.lower().strip()

    for d in data:
        existing_title = d.get('title')
        if isinstance(existing_title, list):
            existing_title = " ".join(existing_title)
        if isinstance(existing_title, str) and title == existing_title.lower().strip():
            return False

    return True

def embed_and_save_papers_with_openai(papers, query, output_dir):
    data = []

    # Ensure papers is a list
    if not isinstance(papers, list):
        print(f"Error: 'papers' is not a list. Type: {type(papers)}")
        return

    # Loop through papers and check their structure
    for idx, paper in enumerate(papers):
        if not isinstance(paper, dict):
            print(f"Skipping non-dict paper at index {idx}: {paper}")
            continue

        title = paper.get('title')
        abstract = paper.get('abstract')

        # Convert title from list to string if needed
        if isinstance(title, list):
            title = " ".join(title)
            paper['title'] = title

        if not isinstance(title, str) or not isinstance(abstract, str):
            print(f"Skipping paper at index {idx} due to invalid title or abstract. Title: {title}, Abstract: {abstract}")
            continue

        if is_title_already_in_data(paper, data):
            data.append(paper)

    st.write(f"Found {len(data)} valid papers about {query} for embedding")

    if not data:
        print("No valid papers found for embedding.")
        return

    data_for_embedding = [f"Title: {d['title'].strip()} ; Abstract: {d['abstract'].strip()}" for d in data]

    try:
        # Use the new embeddings method in v1.0.0+
        response = openai.embeddings.create(
            input=data_for_embedding,
            model="text-embedding-ada-002"  # Adjust model as needed
        )

        # Access response data using dot notation
        text_embedding_tuplist = [
            (text['title'], text['abstract'], text.get('link', ''), np.array(embedding.embedding))
            for text, embedding in zip(data, response.data)
        ]

        pickle_output_path = os.path.join(output_dir, query, f'{query}_embeddings.pkl')
        os.makedirs(os.path.dirname(pickle_output_path), exist_ok=True)

        with open(pickle_output_path, 'wb') as f:
            pickle.dump(text_embedding_tuplist, f)

        st.write(f"Text Embedding Done! Saved to {pickle_output_path}")
        return text_embedding_tuplist

    except Exception as e:
        print(f"Error during embedding creation: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', dest='query', type=str, help='Query to search')
    args = parser.parse_args()

    query = args.query
    output_dir = 'Data'
    
    # Load papers from the specified source
    papers = load_papers(query, output_dir)
    
    # Debug: Print the number of papers loaded
    print(f"Loaded {len(papers)} papers for the query '{query}'")
    
    # Print the structure of the first few papers to understand the issue
    if papers:
        print("First few papers loaded:")
        for i, paper in enumerate(papers[:5]):
            print(f"Paper {i+1}: {paper}")

    # Check if papers were loaded correctly
    if not papers:
        print("No papers found or failed to load papers.")
    else:
        embed_and_save_papers_with_openai(papers, query, output_dir)