import json
import os
from openai import OpenAI
from openpyxl import Workbook

# 1. write precise prompt：emphasizing on negative emotions
SYSTEM_MESSAGE = """Analyze the emotional content of the text.
Focus on identifying negative emotions: "anger", "fear", "sadness", "disgust".
If the text expresses one of these, label it. 
If it is positive, neutral, or a different emotion (like joy or surprise), label it as "other".

Output STRICTLY in JSON format:
{"main_emotion": "anger", "intensity": "high"}
"""

def analyze_negative_sentiment(text, speaker, client):
    # Try reading from the environment variable first
    # api_key = os.getenv("OPENAI_API_KEY")
    
    # If the environment variable is empty, paste your key directly below (for local testing only — be careful not to share it with others)
    # if not api_key:
    api_key = "" # Please aste your Key here
    
    client = OpenAI(api_key=api_key)

    """Emotion analysis，if not, return None"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": f"Speaker: {speaker}. Text: {text}"},
            ],
            response_format={"type": "json_object"}
        )
        res = json.loads(response.choices[0].message.content)
        
        # filter: keep only the target negative emotions
        target_emotions = ["anger", "fear", "sadness", "disgust"]
        if res.get("main_emotion") in target_emotions:
            return res
        return None 
    except Exception as e:
        print(f"API Error: {e}")
        return None

def process_negative_sentiments(input_file, output_file):
    # initialize OpenAI (make sure the environment variable is set)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # prepare Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Negative Sentiments"
    # write the headers you need
    ws.append(["ID", "Speaker", "Clean Text", "Negative Emotion", "Season", "Episode"])

    print(f"Total lines to scan: {len(data)}")
    count = 0

    # to save Token and test，add data[:100]
    for entry in data:
        clean_text = entry.get("clean_text", "")
        speaker = entry.get("speaker", "Unknown")
        
        if not clean_text or len(clean_text) < 5: # skip texts that are too short to be meaningful
            continue
            
        analysis = analyze_negative_sentiment(clean_text, speaker, client)
        
        # only write to Excel when the result is a negative emotion
        if analysis:
            ws.append([
                entry.get("id"),
                speaker,
                clean_text,
                analysis.get("main_emotion"),
                entry.get("season"),
                entry.get("episode")
            ])
            count += 1
            print(f"Found {analysis.get('main_emotion')} for ID {entry.get('id')}")

    wb.save(output_file)
    print(f"\nCompleted! Found {count} negative instances. Saved to {output_file}")

if __name__ == "__main__":
    # run
    process_negative_sentiments("derry_girls_metadata_new.json", "derry_girls_negative_analysis.xlsx")
