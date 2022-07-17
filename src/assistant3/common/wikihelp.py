"""All helping functions for Wikipedia plugin"""

import wikipedia

def wiki_search(text):
    result = wikipedia.search(text, results=4)
    return result

def wiki_summary(text):
    final_result = wikipedia.summary(text, sentences=2)
    return final_result
