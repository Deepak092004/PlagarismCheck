import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
from collections import Counter

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))

# Load semantic model once
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


class PlagiarismEngine:

    # Text Preprocessing
    @staticmethod
    def preprocess(text):
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in STOP_WORDS]
        return tokens

    # Split into chunks (for internet search)
    @staticmethod
    def split_into_chunks(text, chunk_size=150):
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.split()) > 30:
                chunks.append(chunk)

        return chunks

    # Split into sentences
    
    @staticmethod
    def split_into_sentences(text):
        return sent_tokenize(text)

    # TF-IDF Similarity
    
    @staticmethod
    def tfidf_similarity(text1, text2):
        if not text1.strip() or not text2.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform([text1, text2])
            score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(score)
        except:
            return 0.0

    # Jaccard Similarity
    
    @staticmethod
    def jaccard_similarity(text1, text2):
        tokens1 = set(PlagiarismEngine.preprocess(text1))
        tokens2 = set(PlagiarismEngine.preprocess(text2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union)

    # Sequence Similarity
    
    @staticmethod
    def sequence_similarity(text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()

    # Final Combined Score
    
    @staticmethod
    def final_score(text1, text2):
        tfidf = PlagiarismEngine.tfidf_similarity(text1, text2)
        jaccard = PlagiarismEngine.jaccard_similarity(text1, text2)
        sequence = PlagiarismEngine.sequence_similarity(text1, text2)

        final = (0.4 * tfidf) + (0.3 * jaccard) + (0.3 * sequence)
        return round(final * 100, 2)

    # N-Gram Similarity
    
    @staticmethod
    def ngram_similarity(text1, text2, n=3):

        def get_ngrams(text):
            tokens = re.findall(r'\w+', text.lower())
            return set(tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1))

        ngrams1 = get_ngrams(text1)
        ngrams2 = get_ngrams(text2)

        if not ngrams1 or not ngrams2:
            return 0.0

        return len(ngrams1 & ngrams2) / len(ngrams1)

    # Semantic Similarity (Paraphrase Detection)
    @staticmethod
    def semantic_similarity(text1, text2):

        embeddings = semantic_model.encode(
            [text1, text2],
            convert_to_tensor=True,
            show_progress_bar=False
        )

        score = util.cos_sim(embeddings[0], embeddings[1]).item()

        return round(max(0, score) * 100, 2)
