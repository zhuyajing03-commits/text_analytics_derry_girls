import pandas as pd
import spacy

# 1. Read raw data
df = pd.read_excel("derry_girls_negative_analysis.xlsx")

# 2. Extract 25 items for each negative emotion type
sample = (df.groupby("Negative Emotion", group_keys=False)
            .apply(lambda g: g.sample(min(len(g), 25), random_state=42)))

# 3. Scatter the extracted data to prevent over-concentration information
sample = sample.sample(frac=1, random_state=42).reset_index(drop=True)

# 4. Automatical POS annotations
# Load spaCy English pre-trained model (need to run in terminal in advance: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def text_pos_tagger(text):
    if pd.isna(text):
        return ""
    doc = nlp(str(text))
    # Convert text into "word/part of speech" format, for example: "I/PRON love/VERB comedy/NOUN"
    return " ".join([f"{token.text}/{token.pos_}" for token in doc])

# Run POS tagging on the Clean Text and save the results to a new column
sample["POS Tags"] = sample["Clean Text"].apply(text_pos_tagger)

# 5. Save to the new Excel file
output_filename = "negative_analysis_manual_examination.xlsx"
sample.to_excel(output_filename, index=False)

print(f"Successfully generated samples with POS labeling: {output_filename}")
