from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import re

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

    results = [(documents[idx], similarities[0][idx]) for idx in best_indices
               if similarities[0][idx] > 0.4 and len(documents[idx]) > 50]
    return [doc for doc, score in results]

def preprocess_retrieved_docs(docs):
    cleaned_docs = []
    for doc in docs:
        if "Chapter" in doc or doc.strip().isdigit():
            continue
        cleaned_docs.append(doc)
    return cleaned_docs

def extract_figure_numbers(text):
    patterns = [
        r'Figure\s+(\d+-\d+)',   # Matches only hyphenated figures like 'Figure 1-1'
        r'Fig\.\s*(\d+-\d+)',    # Matches 'Fig. 1-1'
        r'FIG\.\s*(\d+-\d+)'     # Matches 'FIG. 1-1'
        r'Figure\s*D(\d+)',      # Matches 'Figure D1', 'Figure D17', etc.
        r'Fig\.\s*D(\d+)',       # Matches 'Fig. D17'
        r'FIG\.\s*D(\d+)',       # Matches 'FIG. D17'
        r'Figure\s*([A-Z]\d+)'   # Matches any alphanumeric figures like 'Figure A1'
    ]

    figure_numbers = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        figure_numbers.extend([match.group(1) for match in matches])

    # Debug printing
    print(f"Debug: Text being searched: {text}")
    print(f"Debug: Found figure numbers: {figure_numbers}")

    return list(set(figure_numbers))

def find_figure_file(figure_number, figures_folder):
    """Enhanced figure file finding with exact naming convention as shown in the images"""
    extensions = ['.png', '.jpg', '.jpeg', '.gif']
    
    # Match exact naming convention shown in the images
    patterns = [
        f'Figure {figure_number}',  # The exact format shown in the images
        f'Figure_{figure_number}',  # Alternative with underscore
        f'Figure{figure_number}',   # Alternative without space
        # Special handling for D-series figures
        f'Figure D{figure_number}' if figure_number.isdigit() else f'Figure {figure_number}',
        # Add variations with different spacings
        f'Figure  {figure_number}',  # Double space
        f'Figure-{figure_number}'    # With hyphen
    ]

    print(f"\nDebug: Searching for figure {figure_number}")
    print(f"Debug: Looking in folder: {figures_folder}")

    # First verify the folder exists
    if not os.path.exists(figures_folder):
        print(f"Debug: Figures folder does not exist: {figures_folder}")
        return None

    # List all files in the directory for debugging
    print("Debug: Files in directory:")
    for file in os.listdir(figures_folder):
        print(f"  {file}")

    for pattern in patterns:
        for ext in extensions:
            potential_file = os.path.join(figures_folder, pattern + ext)
            print(f"Debug: Trying path: {potential_file}")
            if os.path.exists(potential_file):
                print(f"Debug: Found file: {potential_file}")
                return potential_file

    # If exact matches fail, try case-insensitive partial matching
    figure_number_lower = figure_number.lower()
    for file in os.listdir(figures_folder):
        if figure_number_lower in file.lower():
            return os.path.join(figures_folder, file)

    print(f"Debug: No matching file found for figure {figure_number}")
    return None

def display_figures(answer, figures_folder):
    print(f"\nDebug: Searching for figures in folder: {figures_folder}")
    figure_numbers = extract_figure_numbers(answer)
    print(f"Debug: Extracted figure numbers: {figure_numbers}")
    
    displayed_figures = []
    not_found_figures = []

    if figure_numbers:
        plt.figure(figsize=(15, 10))
        num_figures = len(figure_numbers)
        cols = min(2, num_figures)
        rows = (num_figures + cols - 1) // cols

        for idx, fig_num in enumerate(figure_numbers, 1):
            figure_path = find_figure_file(fig_num, figures_folder)
            print(f"Debug: Searching for Figure {fig_num}")
            print(f"Debug: Found path: {figure_path}")

            if figure_path:
                try:
                    img = Image.open(figure_path)
                    plt.subplot(rows, cols, idx)
                    plt.imshow(img)
                    plt.axis('off')
                    plt.title(f'Figure {fig_num}')
                    displayed_figures.append(fig_num)
                    print(f"Debug: Successfully loaded Figure {fig_num}")
                except Exception as e:
                    not_found_figures.append(fig_num)
                    print(f"Debug: Error displaying Figure {fig_num}: {str(e)}")
            else:
                not_found_figures.append(fig_num)
                print(f"Debug: Could not find file for Figure {fig_num}")

        if displayed_figures:
            plt.tight_layout()
            plt.show(block=True)
            plt.close()

        if displayed_figures:
            answer += f"\n\nDisplayed Figures: {', '.join(['Figure ' + num for num in displayed_figures])}"
        if not_found_figures:
            answer += f"\n\nNote: Could not display the following figures: {', '.join(['Figure ' + num for num in not_found_figures])}"

    return answer

def generate_answer(query, retrieved_docs, figures_folder):
    context = " ".join(preprocess_retrieved_docs(retrieved_docs))
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
        do_sample=True  # Changed to True to avoid warnings
    )

    answer = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)

    if figure_references:
        answer += "\n" + "You can refer to the following figure(s) for more details: " + ", ".join(figure_references)

    answer = display_figures(answer, figures_folder)
    return answer.strip()

def preprocess_query(query):
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

def is_greeting(query):
    greetings = ["hello", "hey", "good morning", "good afternoon", "good evening"]
    return any(greet in query.lower() for greet in greetings)

def interactive_qa(figures_folder):
    print("\n🤖 Welcome to the Enhanced Risk Management Q&A System!")
    print("Type 'exit' to quit the program.")
    print("Feel free to ask any questions, and I'll provide the best answer based on my knowledge!\n")

    while True:
        query = input("❓ Enter your question: ").strip()

        if query.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Thank you for chatting! Goodbye!")
            break

        if is_greeting(query):
            print("\n👋 Hello! I'm your guide in risk management, and I'm glad to help you with any questions about this topic!\n")
            continue

        enhanced_query = preprocess_query(query)
        retrieved_docs = retrieve(enhanced_query)

        if not retrieved_docs:
            print("🤖 I'm focused on risk management. I couldn't find relevant information on that topic. Please try a question related to risk management.")
            continue

        response = generate_answer(query, retrieved_docs, figures_folder)
        print("\n📝 Answer:", response, "\n")

if __name__ == "__main__":
    figures_folder = r"/AI_extracted_images"
    
    # Verify folder exists before starting
    if not os.path.exists(figures_folder):
        print(f"Error: Figures folder not found at {figures_folder}")
        print("Please make sure the folder exists and contains your figures.")
        exit(1)
    else:
        print(f"Found figures folder at: {figures_folder}")
        print("Contents of figures folder:")
        for file in os.listdir(figures_folder):
            print(f"  {file}")
    
    interactive_qa(figures_folder)