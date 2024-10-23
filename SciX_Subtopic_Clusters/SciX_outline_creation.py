import json
import os
from openai import OpenAI
import argparse

# Initialize OpenAI client
client = OpenAI(api_key='YOUR-API-KEY')

def clean_response_content(content):
    """
    Clean the response content by removing code block markers and extra whitespace.
    """
    if content.startswith('```json'):
        content = content[7:]  # Remove the opening ```json
    if content.endswith('```'):
        content = content[:-3]  # Remove the closing ```
    return content.strip()

def generate_outline(subtopic_and_cluster_ids, query, output_dir, number_of_chapters=8):
    # Filter subtopics that are marked as related
    subtopic_and_cluster_ids = {k: {'Subtopic': v['Subtopic'], 'Description': v['Description']}
                                for k, v in subtopic_and_cluster_ids.items()
                                if v != 'Removed' and v['Is Related'] == 'RELATED'}

    sys_content = f"""You are given a nested dictionary where each key is a subtopic_id and the value is a dictionary of subtopics of the topic "{query}". Reflect on the subtopics and their descriptions and define clusters of topics that group the subtopics into meaningful research clusters. Create the clusters as an outline where each cluster is a foundational chapter about "{query}". Those clusters will be used by a user to navigate between different domains of the research topic. Give each topic a clear label and describe the subtopics that the cluster is dealing with. Output must be in JSON. Do not leave any subtopic without a cluster.

    ## Output
    - Output a JSON object with:
      - clusters: list of dictionaries with digits from '1' to 'N' containing "cluster_ids", "cluster_title", and "description".
      - subtopics: dictionary with the subtopic_id as a field and the appropriate cluster id as a key for each subtopic in the input.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[
                {"role": "system", "content": sys_content.strip()},
                {"role": "user", "content": f"Subtopic dictionary: {subtopic_and_cluster_ids}"}
            ]
        )

        response_content = response.choices[0].message.content
        response_content = clean_response_content(response_content)

        try:
            outline = json.loads(response_content)
            if 'clusters' not in outline or 'subtopics' not in outline:
                print("Error: The response does not contain the expected 'clusters' or 'subtopics' fields.")
                print("Response content:", response_content)
                return None

            print("Outline generated successfully!")
            return outline

        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON response from the API: {e}")
            print("Response content after cleaning:", response_content)
            return None

    except Exception as e:
        print(f"Error during API call: {e}")
        return None

# def parse_outline(outline, subtopic_and_cluster):
#     if outline is None:
#         print("No outline to parse.")
#         return None

#     map_cluster_id_to_title = {i['cluster_id']: {'title': i['cluster_title'], 'description': i['description']}
#                                for i in outline['clusters']}

#     parsed_outline = {}

#     # Iterate through each subtopic and cluster assignment
#     for subtopic_id, cluster_id in outline['subtopics'].items():
#         cluster_title = map_cluster_id_to_title[cluster_id]['title']
#         if cluster_title not in parsed_outline:
#             parsed_outline[cluster_title] = {
#                 'cluster_id': [subtopic_id],
#                 'description': map_cluster_id_to_title[cluster_id]['description'],
#                 'subtopics': [subtopic_and_cluster[subtopic_id][0]]
#             }
#         else:
#             parsed_outline[cluster_title]['cluster_id'].append(subtopic_id)
#             parsed_outline[cluster_title]['subtopics'].append(subtopic_and_cluster[subtopic_id][0])

#     return parsed_outline
    
def parse_outline(outline, subtopic_and_cluster):
    if outline is None:
        print("No outline to parse.")
        return None

    map_cluster_id_to_title = {str(i['cluster_id']): {'title': i['cluster_title'], 'description': i['description']}
                               for i in outline['clusters']}

    parsed_outline = {}

    # Iterate through each subtopic and cluster assignment
    for subtopic_id, cluster_id in outline['subtopics'].items():
        cluster_id_str = str(cluster_id)  # Ensure consistent string format
        if cluster_id_str not in map_cluster_id_to_title:
            print(f"Warning: cluster_id {cluster_id} not found in map.")
            continue

        cluster_title = map_cluster_id_to_title[cluster_id_str]['title']
        if cluster_title not in parsed_outline:
            parsed_outline[cluster_title] = {
                'cluster_id': [subtopic_id],
                'description': map_cluster_id_to_title[cluster_id_str]['description'],
                'subtopics': [subtopic_and_cluster[subtopic_id][0]]
            }
        else:
            parsed_outline[cluster_title]['cluster_id'].append(subtopic_id)
            parsed_outline[cluster_title]['subtopics'].append(subtopic_and_cluster[subtopic_id][0])

    return parsed_outline

def get_outline_for_subtopics(subtopic_and_cluster, query, output_dir):
    output_path = f"{output_dir}/{query}/{query}_outline.json"

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(output_path):
        id_subtopic_dict = {k: v[0] for k, v in subtopic_and_cluster.items()}
        subtopics_outline = generate_outline(id_subtopic_dict, query, output_dir)

        if subtopics_outline is None:
            print("No valid outline generated.")
            return None

        parsed_outline = parse_outline(subtopics_outline, subtopic_and_cluster)

        if parsed_outline is not None:
            # Save to JSON file
            with open(output_path, "w") as f:
                json.dump(parsed_outline, f, indent=4)
            print(f"Outline saved to {output_path}")
        else:
            print("Failed to parse the outline.")
    else:
        with open(output_path, "r") as f:
            parsed_outline = json.load(f)
            print(f"Outline loaded from {output_path}")

    return parsed_outline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', dest='query', type=str, help='Query to search')
    args = parser.parse_args()

    query = 'near-earth asteroids'  # For testing
    output_dir = 'Data'

    # Load clusters with subtopics
    with open(f"{output_dir}/{query}/{query}_clusters_with_subtopics.json") as f:
        cluster_with_subtopics = json.load(f)

    # Generate and save the outline
    outline = get_outline_for_subtopics(cluster_with_subtopics, query, output_dir)
