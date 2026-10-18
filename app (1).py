import os
import requests
import streamlit as st
import whois
from urllib.parse import urlparse

st.set_page_config(
    page_title="ThreatLens",
    page_icon="🛡️",
    layout="wide"
)


def explain_safety(malicious, suspicious):
    if malicious > 0:
        return (
            "High concern: VirusTotal reported malicious detections. "
            "Avoid opening this website unless you can verify it is legitimate."
        )
    elif suspicious > 0:
        return (
            "Caution: Some scanners reported suspicious activity. "
            "Verify the website before interacting with it."
        )
    else:
        return (
            "No malicious detections were reported in this scan. "
            "This does not prove the website is safe. "
            "Check the domain carefully and avoid sharing sensitive information "
            "unless you trust the website."
        )

st.title("🛡️ ThreatLens")
st.subheader("AI-Based Website Safety Checker")
st.write("Check a URL using VirusTotal security reports.")

api_key = os.environ.get("VT_API_KEY", "")

target = st.text_input(
    "Enter a website URL",
    placeholder="https://example.com"
)

if st.button("🔍 Check Safety"):
    if not target.strip():
        st.warning("Please enter a website URL.")
    elif not api_key:
        st.error("API key is missing. Set VT_API_KEY first.")
    else:
        parsed = urlparse(target.strip())
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            st.error("Enter a complete URL, e.g. https://example.com")
        else:
            try:
                domain = parsed.hostname
                st.subheader("Website Information")
                st.write("**Domain:**", domain)

                try:
                    details = whois.whois(domain)
                    created = details.creation_date
                    if isinstance(created, list):
                        created = created[0]
                    st.write("**Creation Date:**", str(created) if created else "Not available")
                    st.write("**Country:**", details.country or "Not available")
                except Exception:
                    st.info("WHOIS details are not available for this domain.")

                headers = {"x-apikey": api_key}
                response = requests.post(
                    "https://www.virustotal.com/api/v3/urls",
                    headers=headers,
                    data={"url": target.strip()},
                    timeout=30
                )

                if response.status_code == 200:
                    analysis_id = response.json()["data"]["id"]
                    report = requests.get(
                        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                        headers=headers,
                        timeout=30
                    )

                    if report.status_code == 200:
                        stats = report.json()["data"]["attributes"].get(
                            "stats", {}
                        )
                        malicious = stats.get("malicious", 0)
                        suspicious = stats.get("suspicious", 0)

                        st.metric("Malicious detections", malicious)
                        st.metric("Suspicious detections", suspicious)

                        st.subheader("🧠 Safety Explanation")
                        st.write(explain_safety(malicious, suspicious))

                        if malicious > 0:
                            st.error("Potential threat detected.")
                        elif suspicious > 0:
                            st.warning("Some scanners reported suspicious activity.")
                        else:
                            st.info(
                                "No malicious detections in this analysis. "
                                "This does not guarantee the URL is safe."
                            )
                    else:
                        st.error(f"Could not retrieve analysis: {report.status_code}")
                else:
                    st.error(
                        f"VirusTotal request failed: {response.status_code}. "
                        "Check your API key and account quota."
                    )
            except requests.RequestException as exc:
                st.error(f"Network request failed: {exc}")

st.caption("ThreatLens is an informational tool, not a guarantee of safety.")
