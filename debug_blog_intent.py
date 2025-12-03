#!/usr/bin/env python3
"""
Debug script to test blog/how-to intent detection
"""

import json
from pathlib import Path

# Load intents
kb_path = Path("data/intent_knowledge_base.json")
with open(kb_path, 'r') as f:
    data = json.load(f)
    intents = data.get('intents', {})

# Test query
test_query = "how-to"
query_lower = test_query.lower()
query_words = set(query_lower.split())

print(f"\n{'='*60}")
print(f"Testing query: '{test_query}'")
print(f"Query words: {query_words}")
print(f"{'='*60}\n")

# Check all intents
results = []
for intent_name, intent_info in intents.items():
    keywords = intent_info.get('keywords', [])
    matched = 0
    matched_keywords = []
    
    for kw in keywords:
        kw_lower = kw.lower()
        # Exact phrase match
        if kw_lower in query_lower:
            matched += 2
            matched_keywords.append(f"'{kw}' (exact: +2)")
        # Partial word match (any word in keyword matches query)
        elif any(word in query_lower for word in kw_lower.split()):
            matched += 1
            matched_keywords.append(f"'{kw}' (partial: +1)")
    
    if matched > 0:
        score = matched / (len(keywords) * 2) if keywords else 0
        score = min(score, 1.0)
        results.append({
            'intent': intent_name,
            'score': score,
            'matched': matched,
            'max_possible': len(keywords) * 2,
            'keywords': keywords,
            'matched_keywords': matched_keywords
        })

# Sort by score
results.sort(key=lambda x: x['score'], reverse=True)

# Display results
print(f"{'Intent':<30} {'Score':<8} {'Matched':<15}")
print("-" * 60)
for r in results[:5]:  # Top 5
    print(f"{r['intent']:<30} {r['score']:.3f}   {r['matched']}/{r['max_possible']}")
    if r['matched_keywords']:
        print(f"  Matched keywords: {r['matched_keywords']}")
    print()

# Check specifically for blog intent
print(f"\n{'='*60}")
print("Checking intent_blog_content specifically:")
print(f"{'='*60}\n")

if 'intent_blog_content' in intents:
    blog_intent = intents['intent_blog_content']
    print(f"Keywords: {blog_intent.get('keywords', [])}")
    print(f"Documents: {blog_intent.get('documents', [])}")
    
    # Check keyword matching manually
    keywords = blog_intent.get('keywords', [])
    for kw in keywords:
        kw_lower = kw.lower()
        exact_match = kw_lower in query_lower
        partial_match = any(word in query_lower for word in kw_lower.split())
        print(f"  '{kw}': exact={exact_match}, partial={partial_match}")

print(f"\nTop match: {results[0]['intent'] if results else 'None'}")
print(f"Top score: {results[0]['score']:.3f}" if results else "N/A")
