"""
data_loader.py
Reads a clinical case file and returns its content cleanly.
"""
import os
import glob


class DataLoader:
    def __init__(self, cases_folder="E:/Oishee/Thesis/cases"):
        self.cases_folder = cases_folder

    def list_cases(self):
        """Return all case file paths."""
        pattern = os.path.join(self.cases_folder, "*.txt")
        return sorted(glob.glob(pattern))

    def load_case(self, filepath):
        """Load one case file and parse its sections."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        case = {
            "filename": os.path.basename(filepath),
            "specialty": self._extract(content, "SPECIALTY:"),
            "condition": self._extract(content, "CONDITION:"),
            "case_name": self._extract(content, "CASE NAME:"),
            "description": self._extract(content, "DESCRIPTION:"),
            "transcription": self._extract_transcription(content),
            "full_text": content,
        }
        return case

    def _extract(self, content, label):
        """Pull a single-line field that starts with label."""
        for line in content.split("\n"):
            if line.startswith(label):
                return line.replace(label, "").strip()
        return ""

    def _extract_transcription(self, content):
        """Pull the transcription block (between TRANSCRIPTION: and KEYWORDS:)."""
        if "TRANSCRIPTION:" in content:
            after = content.split("TRANSCRIPTION:")[1]
            if "KEYWORDS:" in after:
                return after.split("KEYWORDS:")[0].strip()
            return after.strip()
        return content


# Quick test when run directly
if __name__ == "__main__":
    loader = DataLoader()
    cases = loader.list_cases()
    print(f"Found {len(cases)} case files.\n")

    if cases:
        # Load and show the first case
        case = loader.load_case(cases[0])
        print("=" * 60)
        print(f"Filename:    {case['filename']}")
        print(f"Specialty:   {case['specialty']}")
        print(f"Condition:   {case['condition']}")
        print(f"Case name:   {case['case_name']}")
        print(f"Description: {case['description']}")
        print("-" * 60)
        print("Transcription (first 300 chars):")
        print(case['transcription'][:300])
        print("=" * 60)