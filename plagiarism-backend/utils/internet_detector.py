import requests
import re
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from utils.plagiarism_engine import PlagiarismEngine
from config import Config   


class InternetDetector:

    # ✅ LOAD API KEY FROM CONFIG
    
    SERPER_API_KEY = Config.SERPER_API_KEY
    SERPER_URL = "https://google.serper.dev/search"

    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Google Search using Serper
    
    @staticmethod
    def search_web(query, num_results=5):

        if not InternetDetector.SERPER_API_KEY:
            print("❌ SERPER API KEY NOT FOUND")
            return []

        headers = {
            "X-API-KEY": InternetDetector.SERPER_API_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": num_results
        }

        try:
            response = requests.post(
                InternetDetector.SERPER_URL,
                headers=headers,
                json=payload,
                timeout=10
            )

            print("🔍 Search Status Code:", response.status_code)

            if response.status_code != 200:
                print("❌ Search Failed:", response.text)
                return []

            data = response.json()

            links = []

            if "organic" in data:
                for item in data["organic"]:
                    if "link" in item:
                        links.append(item["link"])

            print("✅ Found URLs:", len(links))

            return links

        except Exception as e:
            print("❌ Search error:", e)
            return []

    # Extract clean text from webpage
    @staticmethod
    def extract_text_from_url(url):
        try:
            response = requests.get(url, timeout=8)

            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style", "noscript"]):
                script.extract()

            text = soup.get_text(separator=" ")
            text = re.sub(r"\s+", " ", text)

            return text.lower()

        except Exception:
            return ""

    # Main Internet Plagiarism Detection
    @staticmethod
    def detect_internet_plagiarism(file_text):

        if not file_text or len(file_text.strip()) < 50:
            return {
                "overall_score": 0,
                "matches": [],
                "total_sources_checked": 0,
                "total_matched_sources": 0
            }

        matches = []
        checked_sources = 0

        chunks = PlagiarismEngine.split_into_chunks(file_text)

        print(f"\n Starting Web Scan ({len(chunks)} chunks)")

        # Limit chunks for speed (can increase later)
        
        for chunk in chunks[:3]:

            search_query = chunk[:200]

            urls = InternetDetector.search_web(search_query)

            if not urls:
                print("⚠ No URLs returned from search")

            for url in urls:
                print("🔎 Checking:", url)

                page_text = InternetDetector.extract_text_from_url(url)
                checked_sources += 1

                if not page_text or len(page_text) < 200:
                    continue

                quick_semantic = PlagiarismEngine.semantic_similarity(
                    chunk,
                    page_text[:2000]
                )

                print("Quick semantic score:", quick_semantic)

                if quick_semantic < 35:
                    continue

                file_sentences = PlagiarismEngine.split_into_sentences(chunk)
                page_sentences = PlagiarismEngine.split_into_sentences(page_text)

                for fs in file_sentences:
                    best_score = 0
                    best_match = ""

                    for ps in page_sentences[:100]:
                        ngram_score = PlagiarismEngine.ngram_similarity(fs, ps)

                        if ngram_score < 0.05:
                            continue

                        semantic_score = PlagiarismEngine.semantic_similarity(fs, ps)

                        combined = (ngram_score * 100 * 0.4) + (semantic_score * 0.6)

                        if combined > best_score:
                            best_score = combined
                            best_match = ps

                    if best_score >= 60:
                        matches.append({
                            "source": url,
                            "file_text": fs,
                            "matched_text": best_match,
                            "score": round(best_score, 2)
                        })

        if matches:
            overall_score = round(
                sum(m["score"] for m in matches) / len(matches),
                2
            )
        else:
            overall_score = 0

        print("\n Final Internet Plagiarism:", overall_score, "%")

        return {
            "overall_score": overall_score,
            "matches": matches,
            "total_sources_checked": checked_sources,
            "total_matched_sources": len(set(m["source"] for m in matches))
        }
