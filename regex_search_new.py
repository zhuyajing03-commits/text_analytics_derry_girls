"""Regex-based extraction of Derry (Northern Irish) English dialect features.

The script performs two independent steps:

1. Re-encode the raw script file to UTF-8 (latin-1 is used for reading because
   it maps every byte to a character, so bytes such as 0x85 never raise).
2. Scan a corpus line by line for a set of morphosyntactic dialect features and
   write a report with per-feature counts and sample concordance lines.
"""

import re
from collections import OrderedDict

# --- Configuration ----------------------------------------------------------

RAW_SCRIPT_FILE = "DERRY-GIRLS-SCRIPT.txt"
UTF8_SCRIPT_FILE = "DERRY-GIRLS-SCRIPT-UTF8.txt"

CORPUS_FILE = "Derry_Girls_Corpus_New.txt"
REPORT_FILE = "Derry_Dialect_Features_Results.txt"

# Maximum number of concordance lines printed per feature (counts stay complete).
MAX_SAMPLES_PER_FEATURE = 30

# --- Dialect feature patterns ----------------------------------------------

# Past-tense forms that may follow "never" when it works as a simple negator.
_PAST_FORMS = (
    r"\w+ed|did|went|saw|came|made|took|got|gave|told|seen|heard|done|said"
)

# Perfect-aspect auxiliaries: "have never seen" is standard English, not the
# dialect feature, so those hits are excluded with lookbehinds.
_PERFECT_AUX = (
    r"(?<!\bhave\s)(?<!\bhas\s)(?<!\bhad\s)(?<!'ve\s)(?<!'d\s)(?<!'s\s)"
)

PATTERNS = OrderedDict((
    # 1. "never" as a past-tense negator, i.e. equivalent to "didn't".
    #    e.g. "I never saw him" = "I didn't see him"
    ("Never_Negator", re.compile(
        _PERFECT_AUX + r"\bnever\s+(?:" + _PAST_FORMS + r")\b",
        re.IGNORECASE,
    )),

    # 2. "was" instead of "were" in conditional clauses.
    #    e.g. "If I was you"
    ("Conditional_Was", re.compile(
        r"\bif\s+(?:I|we|you|they|he|she|it|there|(?:the|a|an)\s+\w+)\s+was\b",
        re.IGNORECASE,
    )),

    # 3. Non-standard second-person pronouns.
    #    e.g. "ye", "yous", "yer"
    ("2nd_Person_Pronouns", re.compile(
        r"\b(?:ye|yeh|yer|yous|youse|thou|thee|ya)\b",
        re.IGNORECASE,
    )),

    # 4. "them" used as a demonstrative instead of "those".
    #    e.g. "them things"
    ("Them_Demonstrative", re.compile(
        r"\bthem\s+[a-z]+s\b",
        re.IGNORECASE,
    )),

    # 5. Existential "there" with a singular verb before a plural noun phrase.
    #    e.g. "There's three of them"
    ("Existential_There_Singular", re.compile(
        r"\bthere(?:'s| is| was)\s+"
        r"(?:(?:\d+|two|three|four|five|six|many|several|lots of|loads of"
        r"|plenty of|some)\b|[a-z]+s\b|people|children|men|women)",
        re.IGNORECASE,
    )),
))

# --- Steps ------------------------------------------------------------------


def convert_to_utf8(input_file=RAW_SCRIPT_FILE, output_file=UTF8_SCRIPT_FILE):
    """Re-encode ``input_file`` from latin-1 to UTF-8. Returns True on success."""
    try:
        with open(input_file, "r", encoding="latin-1") as f_in:
            content = f_in.read()
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(content)
    except OSError as exc:
        print(f"Conversion fails: {exc}")
        return False

    print(f"Successful conversion: {output_file}")
    return True


def scan_corpus(input_file, patterns=PATTERNS):
    """Return {feature: [{line, match, context}, ...]} for every pattern hit."""
    results = {feature: [] for feature in patterns}

    with open(input_file, "r", encoding="utf-8") as f_in:
        for line_num, line in enumerate(f_in, 1):
            clean_line = line.strip()
            if not clean_line:
                continue

            for feature, regex in patterns.items():
                for match in regex.finditer(clean_line):
                    results[feature].append({
                        "line": line_num,
                        "match": match.group(),
                        "context": clean_line,
                    })

    return results


def write_report(results, output_file, max_samples=MAX_SAMPLES_PER_FEATURE):
    """Write per-feature counts plus up to ``max_samples`` concordance lines."""
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("=== Derry Girls Full Dialect Feature Report ===\n\n")
        for feature, entries in results.items():
            f_out.write(f"## {feature} (Total Found: {len(entries)})\n")
            f_out.write("-" * 45 + "\n")
            for entry in entries[:max_samples]:
                f_out.write(
                    f"L{entry['line']}: {entry['match']} -> {entry['context']}\n"
                )
            if len(entries) > max_samples:
                f_out.write(
                    f"... {len(entries) - max_samples} more matches not shown\n"
                )
            f_out.write("\n")


def print_summary(results):
    """Print a per-feature hit count overview to stdout."""
    print("feature statistics overview:")
    for feature, entries in results.items():
        print(f"- {feature:30}: {len(entries)} results")


def analyze_derry_dialect_comprehensive(input_file=CORPUS_FILE,
                                        output_file=REPORT_FILE):
    """Scan the corpus, write the report and print the summary."""
    try:
        results = scan_corpus(input_file)
    except FileNotFoundError:
        print(f"Error: input file not found: {input_file}")
        return None

    write_report(results, output_file)
    print(f"Report saved as: {output_file}")
    print_summary(results)
    return results


def main():
    convert_to_utf8()
    analyze_derry_dialect_comprehensive()


if __name__ == "__main__":
    main()
