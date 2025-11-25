from collections import defaultdict
from constants import TECHNOLOGY_TEMPLATES

tech_keywords = defaultdict(set)

common_words_to_avoid = {"is","on","from", "and"}

def tokenize(text):
    return text.lower().split()

for tech, templates in TECHNOLOGY_TEMPLATES.items():
    for template in templates:
        tokens = tokenize(template)
        tokens = [token for token in tokens if token not in common_words_to_avoid]
        tech_keywords[tech].update(tokens)
        tech_keywords[tech].add(tech)



def classify(text):
    tokens = set(tokenize(text))
    # We take the tokens set and use it to match with the keywords set to find how many words are matching
    scores = {tech: len(tokens & keywords) for tech, keywords in tech_keywords.items()} 
    # The highest matching is the closest technology
    best_match = max(scores, key=scores.get)
    return best_match if scores[best_match] > 0 else "unknown"