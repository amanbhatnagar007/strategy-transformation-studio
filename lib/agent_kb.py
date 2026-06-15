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
     "Lifesciences & Healthcare (MedTech, Payer/PBM, providers) with selective cross-sector work. He's created ~$500M "
     "of value for clients, led 100+ engagements, and mentored 150+ professionals. Previously a Decision "
     "Analytics Consultant at ZS Associates."),
    ("How do you size a sales force / design territories?",
     "I size the force to the work, not the other way round. Start from the account universe and the call plan each "
     "segment needs, convert that to capacity, then shape territories for balanced workload and fair earning potential. "
     "I've redesigned commercial structures for a $10B MedTech client — aligning roles, territories and responsibilities "
     "unlocked ~$0.5B of growth — and optimized salesforce deployment on large transactions with 100% placement."),
    ("How do you design incentive compensation?",
     "Pay for what you want more of, keep it simple enough that a rep can do the math in their head. I align the plan to "
     "the commercial strategy — quota structure, payout curves, accelerators — and stress-test for fairness, cost of "
     "sales and unintended behavior. I'm an EY Certified SFE Trainer and ZS Certified IC Design Professional."),
    ("How do you think about pricing and business models?",
     "Price to the value and the buyer's economics, not to cost-plus. In MedTech I've moved clients from capital, "
     "volume-driven pricing into subscription, Solution-as-a-Service and pay-per-use — lowering adoption barriers and "
     "smoothing revenue. One pay-per-use offering grew to ~10% of total company revenue."),
    ("How do you optimize omni-channel / digital marketing?",
     "Map the customer journey, then allocate spend to the channel mix that actually moves behavior, measured by "
     "conversion not activity. For a diabetes client I analyzed interactions across omni digital channels and lifted "
     "physician conversion by ~5%."),
    ("How do you analyze payer contracts / provider profitability?",
     "I look through encounter volumes, service and patient mix, and reimbursement rates to find where contracts make "
     "or lose money, then renegotiate from facts. This drove a ~15% profitability improvement for a large healthcare "
     "provider and smarter, stronger payer relationships."),
    ("What did you do with Medicare Advantage?",
     "I transformed a Medicare Advantage partnership for a leading provider — improving risk capture, optimizing care "
     "management programs, enhancing referral pathways and benchmarking reimbursement across payers — unlocking $20M+ "
     "of upside."),
    ("How do you size a market (TAM/SAM/SOM)?",
     "Top-down for the boundary, bottom-up to make it real, and triangulate. TAM from population and prevalence, SAM "
     "from the addressable, reachable segment, SOM from a defensible share given route-to-market and competition. I keep "
     "the assumptions explicit so a CXO can challenge them."),
    ("How do you run commercial due diligence?",
     "Test the equity story: is the market real and growing, is the right to win durable, and do the projections hold? "
     "I pressure-test the commercial model, pipeline and competitive position, and separate high-confidence value from "
     "execution-dependent upside before it's credited to the deal."),
    ("How can I contact you / work with you?",
     "Email amanbhatnagarmrt@gmail.com or call +91-9811186994. I take on commercial strategy, GTM, M&A and "
     "transformation work — happy to talk through your situation."),
]

# Topics the agent can genuinely speak to — used to avoid hallucinating.
TOPICS = ["go-to-market strategy", "route-to-market (direct vs indirect)", "market prioritization",
          "M&A synergies & due diligence", "cost transformation & org redesign", "sales force sizing",
          "incentive compensation", "pricing & business models", "omni-channel marketing",
          "payer contracts & provider profitability", "Medicare Advantage", "market sizing",
          "HCP churn", "MedTech trends", "and Aman's background"]

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


def _topic_list():
    return "I can speak to: " + ", ".join(TOPICS) + ". Ask me about any of those."


def answer_offline(query):
    hits = retrieve(query, k=2)
    # No-hallucination guardrail: if nothing matches well, say so instead of inventing.
    if not hits or hits[0][2] < 0.06:
        return ("I want to stay accurate, so I only answer from what I actually know about Aman's work. "
                "That question is outside it (or too broad). " + _topic_list())
    out = hits[0][1]
    if len(hits) > 1 and hits[1][2] > 0.12:
        out += "\n\n" + hits[1][1]
    return out


def answer_with_key(query, api_key, history=None, model="claude-haiku-4-5-20251001"):
    """Optional: generate a grounded answer via Anthropic. Falls back on any error."""
    context = "\n\n".join(f"Q: {q}\nA: {a}" for q, a, _ in retrieve(query, k=3))
    if not context:
        return answer_offline(query), None
    sys = ("You are Aman Bhatnagar's strategy assistant. Answer in his voice — crisp, MBB-consultant style, "
           "first person, 2-4 short paragraphs max. CRITICAL: ground every claim ONLY in the provided context. "
           "Never invent numbers, clients, or facts. If the context doesn't cover the question, say so plainly and "
           "point them to the topics you can discuss. Do not fabricate.")
    messages = []
    for role, msg in (history or [])[-4:]:
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": f"Context (the ONLY facts you may use):\n{context}\n\nQuestion: {query}"})
    body = json.dumps({
        "model": model, "max_tokens": 600, "system": sys, "messages": messages,
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
