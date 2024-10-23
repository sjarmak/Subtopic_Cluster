# Subtopic Clustering with Knowledge Navigator Scripts

This set of scripts is adapted from the **Knowledge Navigator** project: [Knowledge Navigator GitHub](https://github.com/katzurik/Knowledge_Navigator/tree/main/Navigator). The scripts perform subtopic clustering for scientific literature based on a given search query, using data from the **NASA ADS** and **OpenAI** APIs.

## Example: Near-Earth Asteroids Query

This guide demonstrates subtopic clustering using the query `"near-earth asteroids"`. You can replace this query with any topic of your choice.

## Setup

### 1. Input the Query
The query needs to be specified in the following scripts:
- `SciX_SearchPapers.py`
- `SciX_Paper_Embeddings.py`
- `SciX_cluster_subtopic.py`
- `SciX_subtopic_aspect_generation.py`
- `SciX_outline_creation.py`

### 2. Add API Keys
- **ADS API Key**: Add your ADS API key to `SciX_SearchPapers.py`.
- **OpenAI API Key**: Add your OpenAI API key to:
  - `SciX_Paper_Embeddings.py`
  - `SciX_subtopic_aspect_generation.py`
  - `SciX_outline_creator.py`

## Script Order and Outputs

To perform the full subtopic clustering process, run the scripts in the following order:

1. **Search for Papers**

  ` python SciX_SearchPapers.py --query "near-earth asteroids" --output_dir "Data/" --max_results 1000`

**Output:** Data/near-earth asteroids/near-earth asteroids.jsonl
This script retrieves the top 1000 papers related to the query from the NASA ADS database.

2. **Generate Embeddings**

`python SciX_Paper_Embeddings.py --query "near-earth asteroids"`

**Output:** Data/near-earth asteroids/near-earth asteroids_embeddings.pkl

This script generates text embeddings for the papers using the OpenAI API.
Cluster Subtopics

`python SciX_cluster_subtopic.py`

**Output:** Data/near-earth asteroids/near-earth asteroids_cluster.json

This script clusters the papers based on their embeddings to identify potential subtopics.

3. **Generate Subtopic Aspects**

`python SciX_subtopic_aspect_generation.py --query "near-earth asteroids"`

**Output:** Data/near-earth asteroids/near-earth asteroids_clusters_with_subtopics.json

This script analyzes each cluster to generate meaningful subtopic aspects, identifying related and unrelated clusters.

4. **Create Outline**

`python SciX_outline_creation.py --query "near-earth asteroids"`

**Output:** Data/near-earth asteroids/near-earth asteroids_outline.json
This script generates a structured outline of the subtopics, providing a comprehensive overview of the clustered papers.

**Notes**
Ensure that the Data directory exists before running the scripts.
Verify that your API keys are valid and have sufficient permissions.
If you encounter issues with API responses, try reducing the number of requested papers or check for rate limits.
This pipeline can be customized and extended to other topics of interest, making it a versatile tool for scientific literature analysis and clustering.
