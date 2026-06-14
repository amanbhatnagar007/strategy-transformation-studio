"""Knowledge base + offline retrieval for Aman's AI Agent.

Default mode = TF-IDF retrieval over a curated KB (no API key, works for everyone).
Optional = if the user pastes an Anthropic API key, generate a richer answer grounded
in the retrieved KB context.
"""
import json
import urllib.request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Curated knowledge, written in Aman's voice / frameworks.
KB = [
    ("How do you approach a go-to-market strategy?",
     "I start with the decision the CXO actually faces, then work backwards. Where to play (segments, "
     "geographies prioritized by attractiveness x ease of entry), how to win (value proposition, route-to-market: "
     "direct vs distributor vs hybrid vs digital), and what it takes (salesforce sizing, incentives, the economics). "
     "I always pressure-test the route against ASP, clinical complexity, buyer fragmentation and digital maturity — "
     "high-ASP clinical products reward a direct force; fragmented, low-touch ones favor channel or digital."),
    ("How do you size M&A synergies?",
     "I split synergies into cost and revenue. Cost synergies — SG&A de-duplication, procurement scale, footprint — "
     "are higher-confidence and front-loaded, so they carry most of the credible value. Revenue synergies "
     "(cross-sell, pricing) are margin-adjusted and execution-dependent, so I diligence them hard before crediting "
     "them. I phase to run-rate over ~3 years, net integration cost, and test synergy NPV against the purchase price. "
     "On Payer/PBM deals I've identified $100M+ this way — pharmacy service models, PBM switching, class-of-trade pricing."),
    ("What's your approach to cost transformation?",
     "Find the structural money first. Spans and layers usually hide the biggest, most durable pool — most orgs run "
     "too many management layers, so moving to a target span removes cost and speeds decisions. Then automation/process, "
     "procurement, and footprint. Sequence quick wins (procurement, spans) in Year 1 to self-fund the program, then "
     "automation and footprint in Years 2-3. At run-rate it flows roughly 1:1 to EBITDA. I led ~$150M of identified "
     "cost improvement for a Fortune-500 healthcare client this way."),
    ("How do you design a route-to-market?",
     "Route-to-market is a fit decision, not a preference. Direct salesforce for high-ASP, clinically complex, "
     "reimbursement-driven products where control matters. Distributor/indirect for fragmented buyers, lower ASP and "
     "fast reach with limited fixed cost. Hybrid — direct in core accounts, channel for the long tail — is the common "
     "scaling answer in MedTech. Digital for transactional, high-digital-maturity buyers. Partnership/OEM when you lack "
     "local presence and need speed."),
    ("How do you prioritize markets / countries?",
     "Score each market on attractiveness (size x growth x access) against ease of entry (regulatory, reimbursement, "
     "channel maturity), then tier into waves. Wave 1 is the top-right — high attractiveness and high ease — to prove "
     "the model and self-fund expansion. For MedTech that's usually the US, then large EU5 and high-growth APAC. "
     "Land and expand: don't spend on Tier-2 until Tier-1 economics are proven."),
    ("What is HCP churn prediction and why does it matter?",
     "It's forecasting which prescribers are likely to reduce or stop prescribing so the field force can intervene "
     "before the Rx drops. The strongest signals are a declining Rx trend, payer friction, open service issues and "
     "rising competitor share — all things a rep can act on. I built a predictive churn model at ZS to trigger timely "
     "rep interventions, which improved retention and field-force effectiveness."),
    ("What business models did you design in MedTech?",
     "I helped top-20 MedTechs move beyond capital, volume-driven models into subscription, Solution-as-a-Service and "
     "pay-per-use. Done right these smooth revenue, lower the customer's adoption barrier, and deepen the relationship — "
     "for one client the new 'pay-per-use' offering grew to ~10% of total company revenue."),
    ("What are the 2025 MedTech trends you see?",
     "Shift from hardware to outcomes and recurring-revenue models; AI-enabled and connected devices; commercial models "
     "that bundle service and data; consolidation in Payer/PBM; and a sharper focus on value-based care and "
     "reimbursement. I co-authored ZS's 2025 MedTech Trends point of view on exactly these themes."),
    ("Who is Aman Bhatnagar?",
     "Aman is a Director at EY-Parthenon with 11+ years across Strategy, GTM, M&A and Transformation — majority in "
     "Lifesciences & Healthcare (MedTech, Payer/PBM, providers) with selective cross-sector work. He's delivered ~$1B "
     "in cumulative client impact, led 100+ engagements, and mentored 150+ professionals. Previously a Decision "
     "Analytics Consultant at ZS Associates."),
]

_QUESTIONS = [q for q, _ in KB]
_vectorizer = TfidfVectorizer(stop_words="english")
_matrix = _vectorizer.fit_transform([q + " " + a for q, a in KB])

SUGGESTED = [
    "How do you approach a go-to-market strategy?",
    "How do you size M&A synergies?",
    "What's your approach to cost transformation?",
    "How do you prioritize markets?",
    "Who is Aman Bhatnagar?",
]


def retrieve(query, k=2):
    qv = _vectorizer.transform([query])
    sims = cosine_similarity(qv, _matrix)[0]
    idx = sims.argsort()[::-1][:k]
    return [(KB[i][0], KB[i][1], float(sims[i])) for i in idx if sims[i] > 0.02]


def answer_offline(query):
    hits = retrieve(query, k=2)
    if not hits:
        return ("I don't have a framed answer for that yet — try one of the suggested questions, "
                "or ask about GTM, route-to-market, M&A synergies, cost transformation, HCP churn, "
                "or MedTech business models.")
    # lead with the best match, optionally add a second supporting note
    out = hits[0][1]
    if len(hits) > 1 and hits[1][2] > 0.12:
        out += "\n\n" + hits[1][1]
    return out


def answer_with_key(query, api_key, model="claude-haiku-4-5-20251001"):
    """Optional: generate a grounded answer via Anthropic. Falls back on any error."""
    context = "\n\n".join(f"Q: {q}\nA: {a}" for q, a, _ in retrieve(query, k=3))
    sys = ("You are Aman Bhatnagar's strategy assistant. Answer in his voice — crisp, MBB-consultant style, "
           "first person. Ground every answer ONLY in the provided context; if it's not covered, say so briefly.")
    body = json.dumps({
        "model": model, "max_tokens": 600,
        "system": sys,
        "messages": [{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type": "application/json", "x-api-key": api_key,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return data["content"][0]["text"], None
    except Exception as e:
        return answer_offline(query), f"Generative call failed ({e}); showing the offline answer instead."
