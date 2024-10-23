import json
import os
from openai import OpenAI
import streamlit as st
import argparse

# Instantiate the OpenAI client
client = OpenAI(api_key='YOUR-API-KEY')

def generate_subtopic_aspects(clusters, query, model="gpt-4o-2024-05-13", chunk_size=30):
    SYSTEM_PROMPT = """
# Task Overview:
You are provided with a general topic and a set of scientific papers retrieved by a lexical search system using this topic as a query. Your task is to analyze how the papers relate to the topic and categorize their relevance.

# Instructions:

Evaluate Relevance: Determine if the papers are directly related to the research topic.

- If they are not related to the research domain or do not address the topic directly, mark them as "NOT RELATED."
- If they are a genuine subtopic of the main topic, mark them as "RELATED."
- If the papers would not be relevant to a user searching for the main topic, consider them not related.
- If the papers do not address an explicit relation to the topic, consider them not related.

# Output Requirements:
Output should be a JSON with the following fields:
Description: Write a summary describing the common subtopic reflected in the research theme of the papers in the group in relation to the Topic. 
Subtopic: Give a title for the group of papers that represents a meaningful subtopic of the Topic.
Relatedness: Rate the relatedness on a scale from 1 to 5, where 1 means not relevant at all, and 5 indicates the papers deal directly with the topic.
Is Related: State whether the papers are "RELATED" or "NOT RELATED" based on their relevance to the original topic.
- Write nothing else
"""

    subtopics = []
    progress_text = f"Generating {query} Aspects. Please wait."
    progress_bar = st.progress(0, text=progress_text)

    for cl, (cluster_id, papers) in enumerate(clusters.items()):
        if len(papers) > 3:
            print(f"\nProcessing cluster {cluster_id} with {len(papers)} papers...\n")

            # Split the papers into smaller chunks
            chunked_subtopics = []
            for i in range(0, len(papers), chunk_size):
                chunk = papers[i:i + chunk_size]
                papers_list = ''
                for j, paper in enumerate(chunk):
                    line = f"\n{j}: {paper['title']}\nAbstract: {paper['abstract']}"
                    papers_list += line

                content = f"Topic: {query}\nPapers: {papers_list}"

                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT.strip()},
                            {"role": "user", "content": content}
                        ]
                    )

                    response_content = response.choices[0].message.content
                    
                    # Debug: Print the raw response for inspection
                    print(f"Cluster {cluster_id} - Chunk Response:\n{response_content}\n")

                    # Clean up the response content
                    if response_content.startswith('```json'):
                        response_content = response_content[7:-3].strip()

                    # Parse the JSON response
                    try:
                        subtopic_json = json.loads(response_content)

                        # Check if the subtopic is marked as "RELATED"
                        if subtopic_json.get("Is Related", "").upper() == "RELATED":
                            chunked_subtopics.append(subtopic_json)
                            print(f"Chunk {i // chunk_size + 1} of Cluster {cluster_id} is marked as RELATED.")
                        else:
                            print(f"Chunk {i // chunk_size + 1} of Cluster {cluster_id} is marked as NOT RELATED.")

                    except json.JSONDecodeError:
                        print(f"Invalid JSON response for chunk {i // chunk_size + 1} of cluster {cluster_id}: {response_content}")

                except Exception as e:
                    print(f"Error generating subtopic for chunk {i // chunk_size + 1} of cluster {cluster_id}: {e}")

            # Merge results from all chunks
            if chunked_subtopics:
                # Combine the descriptions and subtopics into one
                combined_description = ' '.join([subtopic['Description'] for subtopic in chunked_subtopics])
                combined_subtopic = ', '.join([subtopic['Subtopic'] for subtopic in chunked_subtopics])

                # Create a unified response for the cluster
                unified_subtopic_json = {
                    "Description": combined_description,
                    "Subtopic": combined_subtopic,
                    "Relatedness": max(subtopic['Relatedness'] for subtopic in chunked_subtopics),
                    "Is Related": "RELATED"
                }
                subtopics.append(unified_subtopic_json)
                print(f"Cluster {cluster_id} combined result marked as RELATED.")
            else:
                subtopics.append('Removed')
                print(f"Cluster {cluster_id} could not be processed.")

        else:
            print(f"Cluster {cluster_id} skipped due to insufficient papers.")
            subtopics.append('Removed')

        progress_bar.progress(cl + 1, text=progress_text)

    # Update clusters with the generated subtopics
    for i, (cluster_id, titles) in enumerate(clusters.items()):
        if isinstance(subtopics[i], dict):
            clusters[cluster_id] = (subtopics[i], titles)
        else:
            clusters[cluster_id] = ('Removed', titles)

    return clusters

def name_the_clusters(clusters, query, output_dir):
    output_path = f"{output_dir}/{query}/{query}_clusters_with_subtopics.json"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not os.path.exists(output_path):
        clusters_with_subtopics = generate_subtopic_aspects(clusters, query)

        # Save the generated subtopics to a JSON file
        with open(output_path, "w") as f:
            json.dump(clusters_with_subtopics, f, indent=4)
    else:
        with open(output_path, "r") as f:
            clusters_with_subtopics = json.load(f)

    return clusters_with_subtopics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', dest='query', type=str, help='Query to search')
    args = parser.parse_args()

    query = "near-earth asteroids"
    output_dir = 'Data'

    cluster_file = f"{output_dir}/{query}/{query}_cluster.json"
    if os.path.exists(cluster_file):
        with open(cluster_file, "r") as f:
            cluster_output = json.load(f)
    else:
        print(f"Cluster file not found: {cluster_file}")
        exit(1)

    clusters_with_subtopics = name_the_clusters(cluster_output, query, output_dir)
    print(f"Clusters with subtopics saved to {output_dir}/{query}/{query}_clusters_with_subtopics.json")