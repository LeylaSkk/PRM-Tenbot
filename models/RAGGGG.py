from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load models
retriever_model = SentenceTransformer('all-MiniLM-L6-v2')
generator_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
generator_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

# Load and read documents
with open(r'C:\Users\MK 10\OneDrive\Bureau\AI project\processed_text.txt', 'r', encoding="utf-8") as file:
    lemmatized_text = file.read()

# Split documents into sentences or paragraphs
documents = lemmatized_text.split('\n')

# Encode documents for retrieval
document_embeddings = retriever_model.encode(documents)


def retrieve(query, top_n=5):
    query_embedding = retriever_model.encode([query])
    similarities = cosine_similarity(query_embedding, document_embeddings)
    best_indices = np.argsort(similarities[0])[::-1][:top_n]

    # Filter documents to avoid chapter titles or low relevance
    results = [(documents[idx], similarities[0][idx]) for idx in best_indices
               if similarities[0][idx] > 0.4 and len(documents[idx]) > 50]  # Avoid short titles
    return [doc for doc, score in results]


def preprocess_retrieved_docs(docs):
    """Clean retrieved documents to avoid chapter titles."""
    cleaned_docs = []
    for doc in docs:
        if "Chapter" in doc or doc.strip().isdigit():
            continue
        cleaned_docs.append(doc)
    return cleaned_docs


def generate_answer(query, retrieved_docs):
    context = " ".join(preprocess_retrieved_docs(retrieved_docs))

    # Look for figure references in the context
    figure_references = [doc for doc in retrieved_docs if "Figure" in doc]

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
        num_beams=5,
        no_repeat_ngram_size=3,
        temperature=0.5,
        top_k=50,
        top_p=0.85,
        do_sample=False
    )

    answer = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Append figure references to the answer if they exist
    if figure_references:
        figure_text = "You can refer to the following figure(s) for more details: " + ", ".join(figure_references)
        answer += "\n" + figure_text

    return answer.strip()


def preprocess_query(query):
    """Enhance the query only if it appears related to risk management."""
    risk_management_terms = ["risk", "management", "project", "analysis", "plan", "assessment", "stakeholder"]
    if any(term in query.lower() for term in risk_management_terms):
        # Add specific context keywords
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


def is_greeting(query):
    """Identify if the input is a greeting."""
    greetings = ["hello", "hey", "good morning", "good afternoon", "good evening"]
    return any(greet in query.lower() for greet in greetings)


def interactive_qa():
    print("\n🤖 Welcome to the Enhanced Risk Management Q&A System!")
    print("Type 'exit' to quit the program.")
    print("Feel free to ask any questions, and I’ll provide the best answer based on my knowledge!\n")

    while True:
        query = input("❓ Enter your question: ").strip()

        if query.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Thank you for chatting! Goodbye!")
            break

        # Check if the query is a greeting
        if is_greeting(query):
            print("\n👋 Hello! I’m your guide in risk management, and I’m glad to help you with any questions about this topic!\n")
            continue

        # Enhance the query for better results
        enhanced_query = preprocess_query(query)
        retrieved_docs = retrieve(enhanced_query)

        if not retrieved_docs:
            print("🤖 I'm focused on risk management. I couldn't find relevant information on that topic. Please try a question related to risk management.")
            continue

        response = generate_answer(query, retrieved_docs)
        print("\n📝 Answer:", response, "\n")


if __name__ == "__main__":
    interactive_qa()
