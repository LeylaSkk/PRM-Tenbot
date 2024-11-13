import spacy
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Tuple, Dict
import json
import os


class NLPAnalyzer:
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the NLP analyzer with specified spaCy model."""
        self.nlp = spacy.load(model_name)
        self.nlp.max_length = 2000000  # Increase max text length

    def perform_ner(self, text: str) -> List[Dict]:
        """
        Perform Named Entity Recognition with detailed entity information.
        Returns list of dictionaries containing entity details.
        """
        doc = self.nlp(text)
        ner_results = []

        for ent in doc.ents:
            ner_results.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'description': spacy.explain(ent.label_)
            })

        # Count entity frequencies
        entity_counts = Counter(ent['label'] for ent in ner_results)

        return {
            'entities': ner_results,
            'entity_counts': dict(entity_counts)
        }

    def perform_pos(self, text: str) -> List[Dict]:
        """
        Perform enhanced Part-of-Speech tagging with lemmatization and dependency info.
        """
        doc = self.nlp(text)
        pos_results = []

        for token in doc:
            pos_results.append({
                'text': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,
                'tag': token.tag_,
                'dep': token.dep_,
                'pos_description': spacy.explain(token.pos_),
                'tag_description': spacy.explain(token.tag_),
                'is_stop': token.is_stop
            })

        # Count POS tag frequencies
        pos_counts = Counter(item['pos'] for item in pos_results)

        return {
            'tokens': pos_results,
            'pos_counts': dict(pos_counts)
        }

    def calculate_tfidf(self, texts: List[str], **kwargs) -> Dict:
        """
        Calculate TF-IDF with enhanced features and multiple documents support.
        Automatically adjusts parameters based on number of documents.

        Parameters:
        - texts: List of text documents
        - kwargs: Additional parameters for TfidfVectorizer
        """
        # Determine if we're dealing with a single document
        is_single_doc = len(texts) == 1

        # Adjust parameters based on number of documents
        if is_single_doc:
            default_params = {
                'stop_words': 'english',
                'ngram_range': (1, 2),  # Include bigrams
                'max_features': 1000,
                'min_df': 1,  # For single document
                'max_df': 1.0  # For single document
            }
        else:
            default_params = {
                'stop_words': 'english',
                'ngram_range': (1, 2),
                'max_features': 1000,
                'min_df': 2,
                'max_df': 0.95
            }

        # Update default parameters with any provided kwargs
        default_params.update(kwargs)

        # Initialize and fit TF-IDF vectorizer
        vectorizer = TfidfVectorizer(**default_params)
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Get feature names (terms)
        feature_names = vectorizer.get_feature_names_out()

        # Convert to DataFrame for easier manipulation
        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=feature_names
        )

        # Calculate document-wise statistics
        doc_stats = {
            'avg_tfidf': tfidf_matrix.mean(axis=1).A1.tolist(),
            'max_tfidf': tfidf_matrix.max(axis=1).toarray().flatten().tolist(),
            'num_nonzero_terms': (tfidf_matrix != 0).sum(axis=1).A1.tolist()
        }

        # Get top terms for each document
        top_terms = []
        for idx, doc in enumerate(tfidf_df.values):
            term_scores = [(term, score) for term, score in zip(feature_names, doc) if score > 0]
            sorted_terms = sorted(term_scores, key=lambda x: x[1], reverse=True)
            top_terms.append(sorted_terms[:10])  # Top 10 terms per document

        return {
            'tfidf_matrix': tfidf_df,
            'vocabulary': feature_names.tolist(),
            'document_stats': doc_stats,
            'top_terms_per_doc': top_terms
        }

    def analyze_text(self, text: str, save_path: str = None) -> Dict:
        """
        Perform comprehensive text analysis including NER, POS, and TF-IDF.

        Parameters:
        - text: Input text to analyze
        - save_path: Optional path to save results
        """
        # Perform all analyses
        ner_results = self.perform_ner(text)
        pos_results = self.perform_pos(text)
        tfidf_results = self.calculate_tfidf([text])

        # Compile results
        analysis_results = {
            'ner_analysis': ner_results,
            'pos_analysis': pos_results,
            'tfidf_analysis': {
                'top_terms': tfidf_results['top_terms_per_doc'][0],
                'document_stats': {
                    'avg_tfidf': tfidf_results['document_stats']['avg_tfidf'][0],
                    'max_tfidf': tfidf_results['document_stats']['max_tfidf'][0],
                    'unique_terms': tfidf_results['document_stats']['num_nonzero_terms'][0]
                }
            }
        }

        # Create save directory if it doesn't exist
        if save_path:
            os.makedirs(save_path, exist_ok=True)

            # Save detailed results to JSON
            with open(os.path.join(save_path, "analysis_results.json"), 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)

            # Save TF-IDF matrix to CSV
            tfidf_results['tfidf_matrix'].to_csv(os.path.join(save_path, "tfidf_matrix.csv"))

            # Save NER and POS summary to text file
            with open(os.path.join(save_path, "summary.txt"), 'w', encoding='utf-8') as f:
                f.write("Named Entity Recognition (NER) Summary:\n")
                f.write(f"Found {len(ner_results['entities'])} named entities\n\n")

                f.write("Part-of-Speech (POS) Summary:\n")
                f.write(f"Processed {len(pos_results['tokens'])} tokens\n\n")

                f.write("Top 10 terms by TF-IDF score:\n")
                for term, score in tfidf_results['top_terms_per_doc'][0]:
                    f.write(f"{term}: {score:.4f}\n")

            print(f"Results saved to {save_path}")

        return analysis_results


def main():
    # Example usage
    analyzer = NLPAnalyzer()

    # Load your text
    with open('processed_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # Perform analysis
    results = analyzer.analyze_text(text, save_path='output')

    # Print summary
    print("\nAnalysis Summary:")
    print(f"Found {len(results['ner_analysis']['entities'])} named entities")
    print(f"Processed {len(results['pos_analysis']['tokens'])} tokens")
    print("\nTop 10 terms by TF-IDF score:")
    for term, score in results['tfidf_analysis']['top_terms']:
        print(f"{term}: {score:.4f}")


if __name__ == "__main__":
    main()
