# Step 1: Text Input Preprocessing
from nltk.tokenize import sent_tokenize, word_tokenize
from test_connection import api_key

# Load document
with open('/Users/muskaangupta/Documents/NEO4J_PROJECT/sample_document.txt', 'r') as file:
    content = file.read()

# Split into sections
sections = content.split('##')
sections = [section.strip() for section in sections if section.strip()]

# Step 2: Text Summarization using Cohere
from cohere import Client

cohere_api_key = api_key  # Replace with your Cohere API key
client = Client(cohere_api_key)

summaries = []
for section in sections:
    # Check if the section is longer than 250 characters
    if len(section) > 250:
        response = client.summarize(
            text=section,  # Pass the section directly
            model='summarize-xlarge'  # Correct model name for summarization
        )
        summaries.append(response.summary)
    else:
        # If text is too short, just add the original section as the summary
        summaries.append(section)

# Step 3: Entity Extraction using SpaCy
import spacy

# Load the smaller SpaCy model (you can use a larger one like "en_core_web_trf" if required)
nlp = spacy.load("en_core_web_sm")  # Change to "en_core_web_trf" for larger model

entities = []

for section in sections:
    doc = nlp(section)
    entities.append([(ent.text, ent.label_) for ent in doc.ents])

# Step 4: Embedding Generation using SentenceTransformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = [model.encode(section) for section in sections]

# Step 5: Neo4j Graph Construction
from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Ghost@1234"))

# Create sections and their summaries in Neo4j
with driver.session() as session:
    for i, section in enumerate(sections):
        session.run(
            "CREATE (n:Section {id: $id, content: $content, summary: $summary})",
            id=i, content=section, summary=summaries[i]
        )

# Step 6: Query Interface using Streamlit
import streamlit as st

# Set up Streamlit UI
st.title("Document Query Interface")
query = st.text_input("Ask a question about the document:")

# Query handling with Cohere model for answers
if query:
    response = client.generate(
        prompt=query,
        model='command-xlarge',  # Use the appropriate model for answering questions
        max_tokens=1000  # Adjust token length if needed
    )
    st.write(response.generations[0].text)
