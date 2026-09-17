# Convert script
input_file = "DERRY-GIRLS-SCRIPT.txt"
output_file = "DERRY-GIRLS-SCRIPT-UTF8.txt"

try:
    # 1. Read with latin-1 (it can handle characters like 0x85)
    with open(input_file, "r", encoding="latin-1") as f:
        content = f.read()
    
    # 2. Write with utf-8
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successful conversion: {output_file}")
except Exception as e:
    print(f"Conversion fails: {e}")


import re

def analyze_derry_dialect_comprehensive(input_file, output_file):

    patterns = {
       # 1. Never as past tense negator
        "Never_Negator": re.compile(
           r"(?<!\bhave\s)(?<!\bhas\s)(?<!\bhad\s)(?<!'ve\s)(?<!'d\s)(?<!'s\s)\bnever\s+(?:\w+ed|did|went|saw|came|made|took|got|gave|told|seen|heard|done|said)\b", 
            re.IGNORECASE
        ),
        
        # 2. Conditional Was (If I was...)
        "Conditional_Was": re.compile(
            r'\bif\s+(?:I|we|you|they|he|she|it|there|(?:the|a|an)\s+\w+)\s+was\b', 
            re.IGNORECASE
        ),
        
        # 3. Second-person variants (Ye, Yous...)
        "2nd_Person_Pronouns": re.compile(r'\b(?:ye|yeh|yer|yous|youse|thou|thee|ya)\b', re.IGNORECASE),
        
        # 4. Them instead of Those
        "Them_Demonstrative": re.compile(r'\bthem\s+[a-z]+s\b', re.IGNORECASE),

        # 5. Existential There (There's + Plural)
        "Existential_There_Singular": re.compile(
            r"\bthere(?:'s| is| was)\s+(?:(?:\d+|two|three|four|five|six|many|several|lots of|loads of|plenty of|some)\b|[a-z]+s\b|people|children|men|women)",
            re.IGNORECASE
        )
    }

    results = {feature: [] for feature in patterns}

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line: continue

                for feature, regex in patterns.items():
                    for match in regex.finditer(clean_line):
                        results[feature].append({
                            "line": line_num,
                            "match": match.group(),
                            "context": clean_line
                        })

        # Output the final result
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write("=== Derry Girls Full Dialect Feature Report ===\n\n")
            for feature, entries in results.items():
                f_out.write(f"## {feature} (Total Found: {len(entries)})\n")
                f_out.write("-" * 45 + "\n")
                # show at least 30 samples
                for entry in entries[:30]:
                    f_out.write(f"L{entry['line']}: {entry['match']} -> {entry['context']}\n")
                f_out.write("\n")

        print(f"Report saved as: {output_file}")
        print("feature statistics overview:")
        for feature, entries in results.items():
            print(f"- {feature:30}: {len(entries)} results")

    except FileNotFoundError:
        print(f"Error: input file not found {input_file}")

# run analysis
analyze_derry_dialect_comprehensive('Derry_Girls_Corpus_New.txt', 'Derry_Dialect_Features_Results.txt')
