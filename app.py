import json
import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Cynbit AI Discovery Engine", layout="wide")

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
            {"role": "user", "content": client_input}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

st.title("Cynbit AI — Client Discovery & Strategic Blueprint Engine")
st.caption("Pre-Sales Intelligence PoC for Cynbit Technologies | Built by Vivek Dangwal")

default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
with st.sidebar:
    api_key = st.text_input("Groq API Key", value=default_key, type="password")
    mode = st.radio("Input Mode", ["Prospect Website URL", "Client Project Brief"])

if mode == "Prospect Website URL":
    user_input = st.text_input("Enter Prospect Website URL", placeholder="zomato.com")
else:
    user_input = st.text_area("Paste Client Project Requirements", placeholder="We run a 50-person logistics company and want to automate customer support calls and track shipments...")

if st.button("Generate Strategic Blueprint", type="primary"):
    if not api_key or not user_input:
        st.error("Please provide a Groq API Key and enter a URL or project brief.")
    else:
        with st.spinner("Analyzing requirements & mapping Cynbit Technologies solutions..."):
            try:
                context = scrape_site(user_input) if mode == "Prospect Website URL" else f"Project Brief: {user_input}"
                result = generate_blueprint(context, api_key)

                st.subheader("Client Overview")
                st.info(result["client_overview"])

                c1, c2, c3 = st.columns(3)
                c1.metric("AI Automation Score", f"{result['readiness_scores']['ai_automation_opportunity']}/100")
                c2.metric("Software Modernization", f"{result['readiness_scores']['software_modernization']}/100")
                c3.metric("Growth & SEO Potential", f"{result['readiness_scores']['growth_seo_potential']}/100")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Key Bottlenecks Found")
                    for gap in result["identified_bottlenecks"]:
                        st.warning(gap)
                with col2:
                    st.subheader("Recommended Cynbit Roadmap")
                    for item in result["recommended_cynbit_roadmap"]:
                        st.success(f"**{item['service']}**: {item['action']} (*Impact: {item['business_impact']}*)")

                st.subheader("Pre-Call Strategic Overview (Ready to Send)")
                st.text_area("Draft Strategic Overview", result["tailored_discovery_brief"], height=180)
            except Exception as e:
                st.error(f"Error analyzing input: {e}")
