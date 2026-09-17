import pandas as pd
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer # import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction import text 

def clean_text(text):
    """Basic text preprocessing: convert to lowercase and remove punctuation and digits."""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

# ==========================================
# PART 1: Season 1–2 Analysis
# ==========================================

# 1. load the data
with open('derry_girls_metadata_new.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.DataFrame(data)

# 2. pre-processing
df['clean_text'] = df['clean_text'].apply(clean_text)
df_grouped = df.groupby(['season', 'episode'])['clean_text'].apply(lambda x: ' '.join(x)).reset_index()

# 3. defining dialectal stop-words
stop_words = list(text.ENGLISH_STOP_WORDS)
dialect_stops = ['wee', 'aye', 'grand', 'ma', 'da', 'didnt', 'dont', 'im', 'id', 'actually', 'just', 'like', 'gonna', 'got']
stop_words.extend(dialect_stops)

# 4. Pipeline A: TF-IDF keyword extraction (episode-level lexical salience)
tfidf_vec = TfidfVectorizer(
    stop_words=stop_words, 
    max_df=0.7,  
    min_df=1     
)
tfidf_matrix = tfidf_vec.fit_transform(df_grouped['clean_text'])
tfidf_feature_names = tfidf_vec.get_feature_names_out()

print("=== (S1E1-S2E6) TF-IDF Key Words ===")
for i, row in df_grouped.iterrows():
    scores = tfidf_matrix[i, :].toarray().flatten()
    top_indices = scores.argsort()[-5:][::-1]
    top_keywords = [tfidf_feature_names[idx] for idx in top_indices]
    print(f"S{int(row['season'])}E{int(row['episode'])}: {', '.join(top_keywords)}")

# 5. Pipeline B: Construct a raw count matrix for LDA
count_vec_s12 = CountVectorizer(
    stop_words=stop_words,
    max_df=0.7, 
    min_df=1
)
count_matrix_s12 = count_vec_s12.fit_transform(df_grouped['clean_text'])
lda_feature_names_s12 = count_vec_s12.get_feature_names_out()

# 6. S1-S2 Topic Modeling (LDA)
n_topics = 3
lda_s12 = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda_s12.fit(count_matrix_s12)  # <-- # Fit the model using the raw word-count matrix

print(f"\n=== LDA {n_topics} topics (S1E1-S2E6) ===")
for topic_idx, topic in enumerate(lda_s12.components_):
    top_words = [lda_feature_names_s12[i] for i in topic.argsort()[:-7:-1]]
    print(f"theme #{topic_idx + 1}: {', '.join(top_words)}")


# ==========================================
# PART 2: Season 3 Analysis
# ==========================================

# 1. Parse the Season 3 corpus
corpus_path = 'Derry_Girls_S03_Corpus.txt'
episodes_data = []

with open(corpus_path, 'r', encoding='utf-8') as f:
    content = f.read()
    parts = re.split(r'SCENE:\s*\./Derry_Girls_03/Derry\.Girls\.S03E(\d+)\.srt', content)
    
    for i in range(1, len(parts), 2):
        ep_num = parts[i]
        ep_text = parts[i+1].strip()
        ep_text = clean_text(ep_text)
        episodes_data.append({'episode': f"S03E{ep_num}", 'content': ep_text})

df_s3 = pd.DataFrame(episodes_data)

# 2. Pipeline A: TF-IDF keyword extraction for Season 3
tfidf_vec_s3 = TfidfVectorizer(
    stop_words=stop_words,
    max_df=0.8,  
    min_df=1
)
tfidf_matrix_s3 = tfidf_vec_s3.fit_transform(df_s3['content'])
tfidf_feature_names_s3 = tfidf_vec_s3.get_feature_names_out()

print("\n=== (S03E01-E07) TF-IDF Key Words ===")
for i, row in df_s3.iterrows():
    scores = tfidf_matrix_s3[i, :].toarray().flatten()
    top_indices = scores.argsort()[-5:][::-1]
    top_keywords = [tfidf_feature_names_s3[idx] for idx in top_indices]
    print(f"{row['episode']}: {', '.join(top_keywords)}")

# 3. Pipeline B: Construct a raw count matrix for LDA
count_vec_s3 = CountVectorizer(
    stop_words=stop_words,
    max_df=0.8,  # Apply the same filtering criteria as the Season 3 TF-IDF analysis
    min_df=1
)
count_matrix_s3 = count_vec_s3.fit_transform(df_s3['content'])
lda_feature_names_s3 = count_vec_s3.get_feature_names_out()

# 4. Train the LDA model on Season 3
lda_s3 = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda_s3.fit(count_matrix_s3)  # <-- # Use the raw word-count matrix for Season 3

# 5. Display the top topic words for each latent topic
def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        # Sort the topic-word weights and retrieve the indices of the top n_top_words (5) terms
        top_features_ind = topic.argsort()[-n_top_words:][::-1]
        top_features = [feature_names[i] for i in top_features_ind]
        
        print(f"Theme #{topic_idx + 1}:")
        print("  " + ", ".join(top_features))
        print()

# Display the top 5 keywords instead of the top 10
n_top_words = 5

print(f"\n=== (S03E01-E07) LDA Topic Modeling ({n_topics} Topics) ===")
# Note: The feature names passed here are extracted specifically from count_vec_s3 (lda_feature_names_s3)
print_top_words(lda_s3, lda_feature_names_s3, n_top_words=n_top_words)