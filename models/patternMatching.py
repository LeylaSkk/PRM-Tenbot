import re
import spacy
from spacy.matcher import Matcher
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Load pre-trained spaCy model (for English language)
nlp = spacy.load("en_core_web_sm")

# Load the preprocessed text from the file
with open("lemmatized_text_nltk.txt", "r", encoding="utf-8") as file:
    text = file.read()

# ---- Step 1: Perform TF-IDF on the Preprocessed Text ----
# We use scikit-learn's TfidfVectorizer to compute TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_features=20)  # Get the top 20 important words
tfidf_matrix = vectorizer.fit_transform([text])
terms = vectorizer.get_feature_names_out()
tfidf_scores = np.sum(tfidf_matrix.toarray(), axis=0)

# Get the top N important words based on TF-IDF scores
important_words = [terms[i] for i in np.argsort(tfidf_scores)[-20:]]
print(f"Top 20 important words from TF-IDF: {important_words}")

# ---- Step 2: Pattern Matching using Important Words ----
# Convert the entire text to lowercase for case-insensitive matching
text = text.lower()

# Initialize the spaCy matcher
doc = nlp(text)
matcher = Matcher(nlp.vocab)

# Create patterns using the important TF-IDF words
for keyword in important_words:
    pattern = [{"LOWER": keyword}, {"POS": "NOUN"}]  # Keyword followed by a noun
    matcher.add(f"{keyword.upper()}_NOUN_PATTERN", [pattern])

# Apply the matcher to the processed text
matches = matcher(doc)
print(f"Found {len(matches)} matches for TF-IDF-based patterns:")

# ---- Step 3: Save Results to a File ----
with open("pattern_matching_results.txt", "w", encoding="utf-8") as result_file:
    result_file.write(f"Top 20 Important Words from TF-IDF: {important_words}\n")
    result_file.write(f"Matched patterns:\n")
    for match_id, start, end in matches:
        result_file.write(f"{doc[start:end].text}\n")

print("Pattern matching results saved to pattern_matching_results.txt")
