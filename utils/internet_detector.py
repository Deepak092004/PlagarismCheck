import requests
from bs4 import BeautifulSoup
from config import Config
from utils.plagiarism_engine import PlagiarismEngine

class InternetDetector:
    # Serper.dev is a direct Google Search wrapper
    SERPER_URL = "https://google.serper.dev/search"

    @staticmethod
    def extract_chunks(text, chunk_size=40):
        """Extracts significant phrases to search on Google."""
        words = text.split()
        if len(words) < 15:
            return [text]
        
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.split()) >= 10:
                chunks.append(chunk)
        return chunks[:5] # Limit to 5 queries per file to save credits

    @staticmethod
    def search_serper(query):
        """Queries Google via Serper.dev API."""
        headers = {
            'X-API-KEY': Config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            "q": query,
            "num": 5  # Fetch top 5 results for each chunk
        }
        
        try:
            response = requests.post(InternetDetector.SERPER_URL, headers=headers, json=payload, timeout=10)
            data = response.json()
            
            if "organic" not in data:
                print(f"DEBUG: No results for chunk: {query[:30]}...")
                return []

            # Return list of links and snippets
            return [{"link": item["link"], "snippet": item.get("snippet", "")} for item in data["organic"]]
        except Exception as e:
            print(f"❌ Serper API Error: {e}")
            return []

    @staticmethod
    def fetch_page_text(url):
        """Attempts to scrape text from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=7)
            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            text = soup.get_text(separator=" ")
            return " ".join(text.split())
        except:
            return ""

    @staticmethod
    def detect_internet_plagiarism(text):
        """Main detection engine."""
        chunks = InternetDetector.extract_chunks(text)
        matches = []
        checked_urls = set()

        print(f"--- 🌐 Starting Serper Web Scan ({len(chunks)} chunks) ---")

        for chunk in chunks:
            search_results = InternetDetector.search_serper(chunk)

            for result in search_results:
                url = result["link"]
                snippet = result["snippet"]

                if url in checked_urls:
                    continue
                checked_urls.add(url)

                print(f"🔎 Checking Source: {url}")
                page_content = InternetDetector.fetch_page_text(url)

                # STRATEGY: Use full page text if possible. 
                # If site blocks us, use the Snippet Google already provided!
                source_text = page_content if page_content else snippet
                
                if not source_text:
                    continue

                score = PlagiarismEngine.tfidf_similarity(text, source_text)
                percentage = round(score * 100, 2)
                
                is_snippet = "(Snippet match)" if not page_content else ""
                print(f"📊 Similarity: {percentage}% {is_snippet}")

                if percentage > 0.1: # Catch even small matches
                    matches.append({
                        "url": url,
                        "similarity_score": percentage,
                        "source_type": "Web Page" if page_content else "Web Snippet"
                    })

        return sorted(matches, key=lambda x: x["similarity_score"], reverse=True)