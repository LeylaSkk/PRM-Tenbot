from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

app = Flask(__name__)
CORS(app)
figures_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '/AI_extracted_images/'))

# Initialize models globally
print("Loading models...")
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
generator_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
generator_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
print("Models loaded successfully!")

# Load documents
def load_documents():
    try:
        with open('models\processed_text.txt', 'r', encoding="utf-8") as file:
            lemmatized_text = file.read()
        docs = [doc for doc in lemmatized_text.split('\n') if doc.strip()]  # Only keep non-empty lines
        print(f"Loaded {len(docs)} documents")
        return docs
    except FileNotFoundError:
        print("Warning: processed_text.txt not found!")
        return []
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return []

documents = load_documents()
if documents:
    print("Computing document embeddings...")
    document_embeddings = retriever_model.encode(documents)
    print("Document embeddings computed successfully!")
else:
    document_embeddings = None
    print("No documents to compute embeddings for!")

def retrieve(query, top_n=5):
    if not documents or document_embeddings is None:
        print("No documents available for retrieval")
        return []
        
    try:
        query_embedding = retriever_model.encode([query])
        similarities = cosine_similarity(query_embedding, document_embeddings)
        
        if len(similarities[0]) == 0:
            print("No similarities computed")
            return []
            
        best_indices = np.argsort(similarities[0])[::-1][:top_n]
        
        results = []
        for idx in best_indices:
            if idx < len(documents) and similarities[0][idx] > 0.4 and len(documents[idx]) > 50:
                results.append(documents[idx])
        
        print(f"Retrieved {len(results)} relevant documents")
        return results
        
    except Exception as e:
        print(f"Error in retrieve function: {str(e)}")
        return []

def preprocess_retrieved_docs(docs):
    if not docs:
        return []
    
    cleaned_docs = []
    for doc in docs:
        if doc and not ("Chapter" in doc or doc.strip().isdigit()):
            cleaned_docs.append(doc)
    return cleaned_docs

def generate_answer(query, retrieved_docs):
    if not retrieved_docs:
        return {
            "text": "I don't have enough information to answer that question. Please try asking something about risk management.",
            "figures": []
        }
    
    try:
        context = " ".join(preprocess_retrieved_docs(retrieved_docs))
        figure_references = [doc for doc in retrieved_docs if "Figure" in doc]
        
        if not context.strip():
            return {
                "text": "I don't have enough context to provide a meaningful answer.",
                "figures": []
            }
        
        input_text = (
            f"Answer concisely based on risk management information provided.\n\n"
            f"Context: {context}\n\n"
            f"Question: {query}\nAnswer:"
        )
        
        inputs = generator_tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024
        )
        
        outputs = generator_model.generate(
            **inputs,
            max_length=250,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
            no_repeat_ngram_size=3,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            top_k=50   
        )
        
        answer_text = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Add figure URLs to the response if there are any
        figure_urls = []
        if figure_references:
            for figure in figure_references:
                # Extract the figure number more robustly
                figure_number = figure.split("Figure")[1].strip().split()[0]
                
                # Ensure the figure number is clean by removing any trailing punctuation
                figure_number = figure_number.rstrip(")., ")

                # Generate the URL with the cleaned figure number
                figure_url = f"http://localhost:5000/api/figures/Figure%20{figure_number}.png"
                figure_urls.append(figure_url)

        # Only add the figure reference text if there are figures
        final_text = answer_text
        if figure_urls:
            final_text += "\nYou can refer to the following figure(s) for more details:"

        # Print the response for debugging
        print("Generated response:", {"text": final_text, "figures": figure_urls})

        return {
            "text": final_text,
            "figures": figure_urls
        }
        
    except Exception as e:
        print(f"Error in generate_answer: {str(e)}")
        return {
            "text": "I encountered an error while generating the answer. Please try again.",
            "figures": []
        }

def preprocess_query(query):
    if not query:
        return ""
        
    risk_management_terms = ["risk", "management", "project", "analysis", "plan", "assessment", "stakeholder"]
    
    if any(term in query.lower() for term in risk_management_terms):
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

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('message', '').strip()
        
        if not query:
            return jsonify({
                'response': {
                    'text': 'Please provide a message to process.',
                    'figures': []
                },
                'type': 'error'
            }), 400
            
        # Check if it's a greeting
        greetings = ["hello", "hey", "hi", "good morning", "good afternoon", "good evening"]
        if any(greet in query.lower() for greet in greetings):
            return jsonify({
                'response': {
                    'text': "Hello! I'm your guide in risk management. How can I help you today?",
                    'figures': []
                },
                'type': 'greeting'
            })
            
        # Process the query
        print(f"Processing query: {query}")
        enhanced_query = preprocess_query(query)
        retrieved_docs = retrieve(enhanced_query)
        
        if not retrieved_docs:
            return jsonify({
                'response': {
                    'text': "I'm focused on risk management. I couldn't find relevant information for your question. Please try asking something about risk management concepts, processes, or best practices.",
                    'figures': []
                },
                'type': 'no_results'
            })
            
        response = generate_answer(query, retrieved_docs)
        print("Generated response:", response)  # Debug log
        
        # Ensure response has the correct structure
        if isinstance(response, dict):
            if 'text' not in response:
                response = {'text': str(response), 'figures': []}
        else:
            response = {'text': str(response), 'figures': []}
            
        return jsonify({
            'response': response,
            'type': 'answer'
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'response': {
                'text': 'An error occurred while processing your request. Please try again.',
                'figures': []
            },
            'type': 'error'
        }), 500 

@app.route('/api/figures/<path:filename>', methods=['GET'])
def serve_figure(filename):
    # Replace %20 with spaces to match the actual filename
    filename = filename.replace("%20", " ")
    figures_folder = os.path.abspath("frontend/public/AI_extracted_images")
    figure_path = os.path.join(figures_folder, filename)
    
    print(f"Attempting to serve file from path: {figure_path}")  # Debug statement

    if os.path.exists(figure_path):
        print("File exists and will be served.")
        return send_file(figure_path)
    else:
        print("File not found!")
        return jsonify({'error': f'Figure not found: {filename}'}), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'documents_loaded': len(documents) if documents else 0,
        'embeddings_computed': document_embeddings is not None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)