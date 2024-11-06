from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load models
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
generator_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
generator_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Load and read documents
with open(r'C:/Users/Zaineb/Downloads/lemmatized_text_nltk.txt', 'r', encoding="utf-8") as file:
    lemmatized_text = file.read()
documents = lemmatized_text.split('\n')
document_embeddings = retriever_model.encode(documents)

# Define functions
def retrieve(query, top_n=5):
    query_embedding = retriever_model.encode([query])
    similarities = cosine_similarity(query_embedding, document_embeddings)
    best_indices = np.argsort(similarities[0])[::-1][:top_n]
    results = [(documents[idx], similarities[0][idx]) for idx in best_indices 
               if similarities[0][idx] > 0.4 and len(documents[idx]) > 50]
    return [doc for doc, score in results]

def preprocess_retrieved_docs(docs):
    cleaned_docs = [doc for doc in docs if "Chapter" not in doc and not doc.strip().isdigit()]
    return cleaned_docs

def generate_answer(query, retrieved_docs):
    context = " ".join(preprocess_retrieved_docs(retrieved_docs))
    input_text = (
        f"Answer concisely based on risk management information provided.\n\n"
        f"Context: {context}\n\n"
        f"Question: {query}\nAnswer:"
    )
    inputs = generator_tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=1024)
    outputs = generator_model.generate(
        **inputs, max_length=250, num_beams=5, no_repeat_ngram_size=3, temperature=0.5, top_k=50, top_p=0.85, do_sample=False
    )
    answer = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer.strip()

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    query = data.get('question', '')
    enhanced_query = preprocess_query(query)
    retrieved_docs = retrieve(enhanced_query)
    
    if not retrieved_docs:
        return jsonify({"answer": "No relevant information found. Please try rephrasing your question."})
    
    answer = generate_answer(query, retrieved_docs)
    return jsonify({"answer": answer})

def preprocess_query(query):
    risk_topics = {
        "who": "responsible parties, accountability, roles",
        "what": "definition, description, explanation",
        "how": "process, methodology, implementation",
        "when": "timeline, frequency, schedule",
        "why": "purpose, reasoning, justification",
        "where": "location, scope, application",
        "monte carlo": "risk quantification, probabilistic analysis",
        "project management": "risk planning, risk assessment"
    }
    query_words = query.lower().split()
    for word in query_words:
        if word in risk_topics:
            query = f"{query} {risk_topics[word]}"
    return query

if __name__ == '__main__':
    app.run(debug=True)
