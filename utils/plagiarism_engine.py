import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


class PlagiarismEngine:

    @staticmethod
    def preprocess(text):
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        return tokens

    @staticmethod
    def tfidf_similarity(text1, text2):
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return score

    @staticmethod
    def jaccard_similarity(text1, text2):
        tokens1 = set(PlagiarismEngine.preprocess(text1))
        tokens2 = set(PlagiarismEngine.preprocess(text2))

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        if len(union) == 0:
            return 0

        return len(intersection) / len(union)

    @staticmethod
    def sequence_similarity(text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()

    @staticmethod
    def final_score(text1, text2):
        tfidf = PlagiarismEngine.tfidf_similarity(text1, text2)
        jaccard = PlagiarismEngine.jaccard_similarity(text1, text2)
        sequence = PlagiarismEngine.sequence_similarity(text1, text2)

        # weighted average
        final = (0.4 * tfidf) + (0.3 * jaccard) + (0.3 * sequence)

        return round(final * 100, 2)
