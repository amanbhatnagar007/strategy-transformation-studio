# Aman Bhatnagar — Strategy & Transformation Studio

A portfolio + interactive app hub built with Streamlit. It showcases functional expertise
(Strategy, GTM, M&A, Transformation) and sector depth in **Lifesciences & Healthcare** (with
selective cross-sector work) through runnable tools that take inputs and return insight.

**No API key required.** AI features run on deterministic consulting frameworks and offline
scikit-learn models. LLM/chat features (later phases) use an *optional* "bring your own key" box.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Home.py
```

## Structure
```
Home.py                       # Portfolio landing + app launcher
pages/                        # One file per mini-app
lib/                          # Shared theme (glassmorphism) + profile/catalog
.streamlit/config.toml        # Dark theme
```

## Deploy (free)
Push to GitHub, then connect the repo at https://share.streamlit.io with `Home.py` as the entry point.

## Roadmap
- **Phase 1 (done):** Studio shell + themed Home + GTM Strategy Builder.
- **Phase 2:** One app per section.
- **Phase 3:** Full 25-app catalog + AI Agent.

Built by Aman Bhatnagar · amanbhatnagarmrt@gmail.com
