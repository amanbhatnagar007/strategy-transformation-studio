"""Market & route-to-market reference data for the GTM Strategy Builder.

Indices are 0-100 directional planning heuristics (not live market data):
  attract = market attractiveness (size x growth x access)
  ease    = ease of entry (regulatory, reimbursement, channel maturity)
"""

# Major target markets by sector. (country, region, attractiveness, ease, growth%)
MARKETS = {
    "MedTech": [
        ("United States", "Americas", 96, 70, 6),
        ("Germany", "Europe", 80, 72, 4),
        ("Japan", "APAC", 78, 55, 3),
        ("China", "APAC", 88, 42, 11),
        ("United Kingdom", "Europe", 70, 68, 4),
        ("France", "Europe", 68, 60, 4),
        ("India", "APAC", 72, 50, 14),
        ("Brazil", "Americas", 60, 45, 7),
        ("Italy", "Europe", 58, 55, 3),
        ("Australia", "APAC", 55, 74, 5),
    ],
    "Pharma": [
        ("United States", "Americas", 98, 62, 6),
        ("China", "APAC", 90, 40, 10),
        ("Japan", "APAC", 80, 52, 2),
        ("Germany", "Europe", 78, 70, 4),
        ("France", "Europe", 70, 60, 3),
        ("United Kingdom", "Europe", 68, 66, 4),
        ("Brazil", "Americas", 62, 44, 8),
        ("India", "APAC", 75, 48, 12),
        ("Italy", "Europe", 60, 54, 3),
        ("Canada", "Americas", 58, 72, 4),
    ],
    "Provider / Hospital": [
        ("United States", "Americas", 95, 58, 5),
        ("Saudi Arabia / GCC", "MEA", 72, 60, 9),
        ("United Kingdom", "Europe", 66, 64, 3),
        ("Germany", "Europe", 70, 66, 3),
        ("India", "APAC", 74, 52, 13),
        ("Australia", "APAC", 60, 72, 5),
        ("Singapore", "APAC", 58, 78, 6),
        ("UAE", "MEA", 64, 66, 8),
    ],
    "Payer / PBM": [
        ("United States", "Americas", 97, 60, 5),
        ("United Kingdom", "Europe", 60, 58, 3),
        ("Germany", "Europe", 64, 62, 3),
        ("Netherlands", "Europe", 56, 70, 3),
        ("Switzerland", "Europe", 58, 64, 3),
        ("Australia", "APAC", 52, 70, 4),
    ],
    "Consumer": [
        ("United States", "Americas", 92, 78, 4),
        ("China", "APAC", 90, 55, 8),
        ("India", "APAC", 85, 60, 12),
        ("United Kingdom", "Europe", 70, 80, 3),
        ("Germany", "Europe", 72, 78, 3),
        ("Brazil", "Americas", 66, 58, 6),
        ("Indonesia", "APAC", 64, 52, 10),
        ("UAE", "MEA", 58, 74, 7),
    ],
    "Other": [
        ("United States", "Americas", 90, 72, 4),
        ("Germany", "Europe", 74, 72, 3),
        ("China", "APAC", 84, 50, 8),
        ("India", "APAC", 78, 58, 11),
        ("United Kingdom", "Europe", 68, 74, 3),
        ("Japan", "APAC", 70, 58, 2),
    ],
}

# Route-to-market archetypes
ROUTES = {
    "Direct sales force": "Own reps sell to clinicians / accounts. Best for high-ASP, clinically complex, "
                          "reimbursement-driven products needing control and deep customer relationships.",
    "Distributor / indirect": "Third-party distributors carry the product. Best for fragmented buyers, "
                              "lower ASP, fast geographic reach with limited fixed cost.",
    "Hybrid (direct + channel)": "Direct in core accounts/markets, channel for the long tail. Balances "
                                 "control with reach — common for scaling MedTech portfolios.",
    "Digital / e-commerce": "Self-serve and tele-sales. Best for transactional, low-touch, "
                            "high-digital-maturity buyers (consumables, consumer-health).",
    "Strategic partnership / OEM": "Co-sell or embed with an established player. Best for new markets, "
                                   "limited local presence, or platform plays.",
}
