import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset with error handling
try:
    df = pd.read_csv("civicmatch_dataset.csv")
except FileNotFoundError:
    raise FileNotFoundError("civicmatch_dataset.csv not found. Please ensure the file exists.")

# Print available columns for debugging
print("Available columns:", df.columns.tolist())

# Detect text column dynamically
TEXT_KEYWORDS = ["description", "details", "info", "summary"]
text_column = None

for keyword in TEXT_KEYWORDS:
    for col in df.columns:
        if keyword.lower() in col.lower():
            text_column = col
            break
    if text_column:
        break

# Fallback: use all columns combined
if not text_column:
    print(f"No text column found with keywords {TEXT_KEYWORDS}. Using all columns combined.")
    text_column = None
    df["combined_text"] = df.astype(str).agg(" ".join, axis=1)
else:
    print(f"Using detected text column: {text_column}")

# Detect scheme_name column dynamically
SCHEME_KEYWORDS = ["scheme_name", "name", "scheme"]
scheme_column = None

for keyword in SCHEME_KEYWORDS:
    for col in df.columns:
        if keyword.lower() in col.lower():
            scheme_column = col
            break
    if scheme_column:
        break

# Fallback: use first column as scheme_name
if not scheme_column:
    scheme_column = df.columns[0]
    print(f"No scheme name column found. Using first column: {scheme_column}")
else:
    print(f"Using detected scheme column: {scheme_column}")

# Combine text if we found a specific text column
if text_column:
    df["combined_text"] = df[scheme_column].astype(str) + " " + df[text_column].astype(str)
else:
    # combined_text already created above
    pass

# Rename scheme_column to scheme_name for consistency
if scheme_column != "scheme_name":
    df["scheme_name"] = df[scheme_column]

# Lazy load model and embeddings on first use
model = None
scheme_embeddings = None

def _initialize_embeddings():
    """Load model and embeddings on first use"""
    global model, scheme_embeddings
    
    if model is not None and scheme_embeddings is not None:
        return  # Already initialized
    
    print("Initializing embeddings on first request...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    scheme_embeddings = model.encode(df["combined_text"].tolist())
    print("Embeddings initialized successfully")

def search_schemes(query):
    try:
        if len(df) == 0:
            return []
        
        # Initialize on first call
        _initialize_embeddings()
        
        query_embedding = model.encode([query])
        scores = cosine_similarity(query_embedding, scheme_embeddings)[0]

        top_indices = scores.argsort()[-3:][::-1]
        results = df.iloc[top_indices].to_dict(orient="records")
        
        # Remove duplicate schemes by scheme_name
        seen = set()
        unique_results = []
        for result in results:
            scheme_name = result.get("scheme_name")
            if scheme_name not in seen:
                seen.add(scheme_name)
                unique_results.append(result)
        
        if len(results) != len(unique_results):
            print(f"Removed {len(results) - len(unique_results)} duplicate scheme(s)")
        
        return unique_results if unique_results else []
    except Exception as e:
        print(f"Error in search_schemes: {e}")
        return []