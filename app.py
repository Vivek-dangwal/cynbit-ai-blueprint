import json
import os
import html
import requests
from bs4 import BeautifulSoup
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Cynbit AI Discovery Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- STYLING -----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(99,102,241,0.25), transparent 40%),
        radial-gradient(circle at 85% 20%, rgba(236,72,153,0.18), transparent 40%),
        radial-gradient(circle at 50% 90%, rgba(34,211,238,0.15), transparent 45%),
        #070b17;
    color: #e2e8f0;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.5rem; max-width: 1200px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.85);
    border-right: 1px solid rgba(148,163,184,0.15);
    backdrop-filter: blur(12px);
}

/* Hero */
.hero {
    position: relative;
    padding: 56px 40px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(99,102,241,0.22), rgba(236,72,153,0.12) 60%, rgba(34,211,238,0.15));
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 25px 80px rgba(79,70,229,0.25);
    overflow: hidden;
    text-align: center;
    margin-bottom: 28px;
}
.hero::before {
    content: ""; position: absolute; inset: -50%;
    background: conic-gradient(from 0deg, transparent, rgba(99,102,241,0.25), transparent 30%);
    animation: spin 12s linear infinite;
}
.hero > * { position: relative; z-index: 1; }
@keyframes spin { to { transform: rotate(360deg); } }
.badge {
    display: inline-block; padding: 6px 16px; border-radius: 999px;
    background: rgba(99,102,241,0.2); border: 1px solid rgba(165,180,252,0.4);
    color: #c7d2fe; font-size: 0.78rem; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 18px;
}
.hero h1 {
    font-size: 3rem; font-weight: 800; line-height: 1.1; margin: 0 0 14px 0;
    background: linear-gradient(90deg, #fff, #a5b4fc 40%, #f0abfc 70%, #67e8f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #94a3b8; font-size: 1.1rem; max-width: 720px; margin: 0 auto; }
.pills { margin-top: 22px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
.pill {
    padding: 6px 14px; border-radius: 999px; font-size: 0.8rem; color: #cbd5e1;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
}

/* Glass cards */
.glass {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 24px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
    margin-bottom: 16px;
}
.glass:hover { transform: translateY(-4px); border-color: rgba(165,180,252,0.45); box-shadow: 0 18px 50px rgba(99,102,241,0.25); }
.section-title {
    font-size: 1.35rem; font-weight: 700; margin: 34px 0 16px 0; color: #f1f5f9;
    display: flex; align-items: center; gap: 10px;
}
.section-title::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(148,163,184,0.4), transparent); }
.overview { font-size: 1.1rem; line-height: 1.7; color: #e2e8f0; border-left: 4px solid #818cf8; }

/* Score rings */
.ring-wrap { text-align: center; }
.ring {
    --p: 0; --c: #818cf8;
    width: 140px; height: 140px; border-radius: 50%; margin: 0 auto 14px auto;
    background: conic-gradient(var(--c) calc(var(--p) * 1%), rgba(148,163,184,0.15) 0);
    display: grid; place-items: center; position: relative;
    box-shadow: 0 0 35px color-mix(in srgb, var(--c) 35%, transparent);
}
.ring::before { content: ""; position: absolute; inset: 12px; border-radius: 50%; background: #0b1120; }
.ring span { position: relative; font-size: 2.1rem; font-weight: 800; color: #fff; }
.ring small { font-size: 0.9rem; color: #94a3b8; font-weight: 500; }
.ring-label { font-weight: 600; color: #cbd5e1; font-size: 0.95rem; }

/* Bottlenecks */
.bottleneck {
    display: flex; gap: 14px; align-items: flex-start; padding: 16px 18px; margin-bottom: 12px;
    border-radius: 14px; background: rgba(251,146,60,0.08); border: 1px solid rgba(251,146,60,0.3);
    color: #fed7aa; transition: transform .2s;
}
.bottleneck:hover { transform: translateX(6px); }
.bottleneck .num {
    min-width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center;
    background: linear-gradient(135deg, #fb923c, #f43f5e); color: #fff; font-weight: 700; font-size: 0.85rem;
}

/* Roadmap */
.road {
    position: relative; padding: 20px 22px 20px 26px; margin-bottom: 14px; border-radius: 16px;
    background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.3);
    transition: transform .2s;
}
.road:hover { transform: translateX(6px); }
.road::before {
    content: ""; position: absolute; left: 0; top: 14px; bottom: 14px; width: 4px; border-radius: 4px;
    background: linear-gradient(180deg, #34d399, #22d3ee);
}
.road .svc { font-weight: 700; color: #6ee7b7; font-size: 1.05rem; margin-bottom: 6px; }
.road .act { color: #e2e8f0; margin-bottom: 10px; line-height: 1.55; }
.road .imp {
    display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 0.8rem;
    background: rgba(34,211,238,0.15); border: 1px solid rgba(34,211,238,0.4); color: #67e8f9;
}

/* Inputs & buttons */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.05) !important; color: #f1f5f9 !important;
    border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129,140,248,0.25) !important;
}
.stButton > button[kind="primary"], .stDownloadButton > button {
    width: 100%; padding: 0.85rem 1.2rem; border-radius: 14px; border: none; font-weight: 700; font-size: 1rem;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); color: #fff;
    box-shadow: 0 10px 30px rgba(168,85,247,0.4); transition: all .25s ease;
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.01); box-shadow: 0 16px 40px rgba(236,72,153,0.5); color: #fff;
}
.footer { text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 50px; padding-bottom: 20px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------- BACKEND -----------------------------
def scrape_site(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2"])[:10]]
    body_text = " ".join(soup.get_text(" ", strip=True).split())[:3000]
    return f"URL: {url}\nTitle: {title}\nHeadings: {headings}\nContent: {body_text}"


def get_active_model(client: Groq) -> str:
    models = [
        m.id for m in client.models.list().data
        if "whisper" not in m.id.lower() and "guard" not in m.id.lower() and "tts" not in m.id.lower()
    ]
    for preferred in ["llama", "qwen", "gemma", "gpt", "mixtral"]:
        for m in models:
            if preferred in m.lower():
                return m
    return models[0]


def generate_blueprint(client_input: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)
    active_model = get_active_model(client)
    system_prompt = """
    You are a Senior AI Solutions Architect at Cynbit Technologies (Jaipur).
    Cynbit's core offerings:
    1. AI Automation (Autonomous Agents, LLM Workflows, AI Voice Agents)
    2. Software Engineering (Next.js, Node.js, FastAPI, Python Web & Mobile Apps)
    3. Cloud Infrastructure (AWS & Azure Deployment & Scaling)
    4. Digital Marketing & Technical SEO (Funnel Optimization, CRM Automation)
    5. SaaS Ecosystem (Cynbit Studio, Revio, TenantEase)

    Analyze the prospect's website or project brief and return STRICT JSON:
    {
      "client_overview": "1-2 sentence summary of the prospect's business",
      "readiness_scores": {
        "ai_automation_opportunity": 85,
        "software_modernization": 75,
        "growth_seo_potential": 70
      },
      "identified_bottlenecks": ["Bottleneck 1", "Bottleneck 2", "Bottleneck 3"],
      "recommended_cynbit_roadmap": [
        {"service": "Exact Cynbit Service Name", "action": "What Cynbit will build", "business_impact": "Expected ROI"}
      ],
      "tailored_discovery_brief": "Concise, high-converting strategic overview ready for Cynbit's pre-sales team to send before a discovery call"
    }
    """
    completion = client.chat.completions.create(
        model=active_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": client_input},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)


# ----------------------------- UI HELPERS -----------------------------
def esc(x) -> str:
    return html.escape(str(x))


def ring(label: str, value, color: str) -> str:
    try:
        v = max(0, min(100, int(value)))
    except (ValueError, TypeError):
        v = 0
    return (
        f'<div class="glass ring-wrap">'
        f'<div class="ring" style="--p:{v};--c:{color}"><span>{v}<small>/100</small></span></div>'
        f'<div class="ring-label">{esc(label)}</div></div>'
    )


# ----------------------------- HERO -----------------------------
st.markdown(
    '<div class="hero">'
    '<div class="badge">Pre-Sales Intelligence • PoC</div>'
    '<h1>Client Discovery &amp;<br>Strategic Blueprint Engine</h1>'
    '<p>Drop in a prospect website or project brief. Get an AI-powered opportunity score, '
    'bottleneck analysis, a tailored Cynbit roadmap and a send-ready discovery brief in seconds.</p>'
    '<div class="pills"><span class="pill">⚡ Groq LLM</span><span class="pill">🌐 Live Site Analysis</span>'
    '<span class="pill">🧭 Roadmap Mapping</span><span class="pill">✉️ Ready-to-Send Brief</span></div>'
    '</div>',
    unsafe_allow_html=True,
)

# ----------------------------- SIDEBAR -----------------------------
default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    api_key = st.text_input("Groq API Key", value=default_key, type="password")
    mode = st.radio("Input Mode", ["Prospect Website URL", "Client Project Brief"])
    st.markdown("---")
    st.markdown("**How it works**")
    st.caption("1. Scrape site / read brief\n\n2. LLM maps needs to Cynbit services\n\n3. Scores, roadmap & brief generated")
    st.markdown("---")
    st.caption("Built by Vivek Dangwal for Cynbit Technologies")

# ----------------------------- INPUT -----------------------------
if mode == "Prospect Website URL":
    user_input = st.text_input("🌐 Prospect Website URL", placeholder="zomato.com")
else:
    user_input = st.text_area(
        "📝 Client Project Requirements",
        placeholder="We run a 50-person logistics company and want to automate customer support calls and track shipments...",
        height=140,
    )

go = st.button("✨ Generate Strategic Blueprint", type="primary")

# ----------------------------- RESULTS -----------------------------
if go:
    if not api_key or not user_input:
        st.error("Please provide a Groq API Key and enter a URL or project brief.")
    else:
        with st.spinner("Analyzing requirements & mapping Cynbit Technologies solutions..."):
            try:
                context = scrape_site(user_input) if mode == "Prospect Website URL" else f"Project Brief: {user_input}"
                result = generate_blueprint(context, api_key)

                st.markdown('<div class="section-title">🏢 Client Overview</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="glass overview">{esc(result.get("client_overview", ""))}</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="section-title">📊 Opportunity Scores</div>', unsafe_allow_html=True)
                scores = result.get("readiness_scores", {})
                c1, c2, c3 = st.columns(3)
                c1.markdown(ring("AI Automation", scores.get("ai_automation_opportunity", 0), "#818cf8"), unsafe_allow_html=True)
                c2.markdown(ring("Software Modernization", scores.get("software_modernization", 0), "#f472b6"), unsafe_allow_html=True)
                c3.markdown(ring("Growth & SEO Potential", scores.get("growth_seo_potential", 0), "#22d3ee"), unsafe_allow_html=True)

                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.markdown('<div class="section-title">⚠️ Key Bottlenecks</div>', unsafe_allow_html=True)
                    bn = "".join(
                        f'<div class="bottleneck"><div class="num">{i}</div><div>{esc(g)}</div></div>'
                        for i, g in enumerate(result.get("identified_bottlenecks", []), 1)
                    )
                    st.markdown(bn, unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="section-title">🚀 Cynbit Roadmap</div>', unsafe_allow_html=True)
                    rd = "".join(
                        f'<div class="road"><div class="svc">{esc(it.get("service", ""))}</div>'
                        f'<div class="act">{esc(it.get("action", ""))}</div>'
                        f'<span class="imp">📈 {esc(it.get("business_impact", ""))}</span></div>'
                        for it in result.get("recommended_cynbit_roadmap", [])
                    )
                    st.markdown(rd, unsafe_allow_html=True)

                st.markdown('<div class="section-title">✉️ Pre-Call Strategic Overview</div>', unsafe_allow_html=True)
                brief = result.get("tailored_discovery_brief", "")
                st.text_area("Draft Strategic Overview (ready to send)", brief, height=200)

                d1, d2 = st.columns(2)
                d1.download_button("⬇️ Download Brief (.txt)", brief, file_name="discovery_brief.txt")
                d2.download_button(
                    "⬇️ Download Full Blueprint (.json)",
                    json.dumps(result, indent=2),
                    file_name="blueprint.json",
                    mime="application/json",
                )
            except Exception as e:
                st.error(f"Error analyzing input: {e}")

st.markdown('<div class="footer">Cynbit AI • Discovery Engine PoC • Built by Vivek Dangwal</div>', unsafe_allow_html=True)
