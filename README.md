# SemanticCube

# Semantic Cube Prototype

This repository contains a prototype implementation for our semantic search system. The goal is to index and aggregate academic papers by multiple dimensions (e.g., time and category) to support efficient, flexible queries using MongoDB’s aggregation pipeline.

## Overview

The prototype consists of two main components:

- **Precomputation (precompute.py):**
  - **Data Ingestion:** Reads a CSV file with paper metadata (ID, title, abstract, update_date, cs_categories, etc.).
  - **Aggregation:** Groups papers by the tuple `(year, month, category)` to create aggregated “cells.” For each cell, it computes:
    - **Paper Count:** The number of papers in that group.
    - **Aggregated Summary:** A concatenated summary of paper abstracts.
    - **Paper IDs:** A list of paper IDs for potential drill-down queries.
  - **Storage:** Individual paper documents are stored in the `papers` collection, and aggregated data is stored in the `semantic_cube` collection.

- **Query Interface (query.py):**
  - **Interactive Filtering:** Provides a command-line interface where users can input a category and optional date ranges (in YYYY-MM format) to query the aggregated data.
  - **Dynamic Pipeline Construction:** Builds a MongoDB aggregation pipeline based on user-specified parameters (category, start date, and end date) and returns aggregated results such as total paper count and summaries.

## How This Prototype Supports Our Project

- **Semantic Indexing & Aggregation:**  
  By precomputing and storing aggregated summaries for each unique combination of time (year and month) and category, the system quickly answers high-level queries. This “semantic cube” design allows us to efficiently roll up data (e.g., combining monthly cells into yearly summaries) or drill down into detailed paper information.

- **Flexible Querying:**  
  The prototype leverages MongoDB’s aggregation pipeline to support both narrow (e.g., specific month and category) and broad (e.g., multiple years) queries. This separation of individual paper storage from aggregated views enables fast responses while preserving detailed data for in-depth analysis.

- **Modular & Extensible Architecture:**  
  Precomputation and query functionalities are separated, allowing for future enhancements such as:
  - Integrating LLMs to generate refined summaries.
  - Expanding dimensions (e.g., adding authors or additional time hierarchies).
  - Dynamically generating query pipelines via natural language processing.
  - Caching frequently used roll-up queries.

## Setup & Usage

1. **Install Dependencies:**
   ```bash
    pip install -r requirements.txt
   ```

3. **Configure MongoDB Connection:**
   - Create a `.env` file in the repository root:
     ```
     MONGODB_URI=mongodb_connection_string
     ```

4. **CSV Data:**
   - Place your CSV file (e.g., `clean_fields_filter_date_sample50.csv`) in the dataset repository.

### Running the Prototype

1. **Precompute Aggregates:**
   ```bash
   python precompute.py
   ```
   This script reads the CSV, parses and aggregates the data, and stores both individual paper documents and the semantic cube in MongoDB.

2. **Query Aggregated Data:**
   ```bash
   python query.py
   ```
   Follow the interactive prompts to filter by category and date ranges (in YYYY-MM format). The system will return aggregated summaries, total paper counts, and other details.

## Future Enhancements

- **Dynamic Query Generation:** Use LLMs to convert natural language queries into MongoDB pipelines.
- **Additional Dimensions:** Expand the semantic cube to include dimensions like authors.
- **Caching Strategies:** Implement caching for commonly requested roll-up queries.
- **LLM-Enhanced Summaries:** Improve the aggregated summaries using advanced LLM techniques.

## Conclusion

This prototype demonstrates a scalable, semantic indexing framework by combining individual paper storage with aggregated views. It serves as a foundation for our semantic search engine, enabling efficient, multi-dimensional queries while preserving detailed paper information for in-depth exploration.
