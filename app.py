
import streamlit as st
from groq import Groq

# -----------------------------------
# 1. Page configuration
# -----------------------------------
st.set_page_config(
    page_title="AI Email Generator",
    page_icon="✉️",
    layout="centered"
)

# -----------------------------------
# 2. Custom styling
# -----------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f7f8fc;
    }

    .hero {
        padding: 25px;
        border-radius: 18px;
        background: linear-gradient(120deg, #4338ca, #7c3aed);
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero p {
        color: white;
        font-size: 16px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 45px;
        font-weight: bold;
    }

    div[data-testid="stDownloadButton"] button {
        width: 100%;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# 3. App heading
# -----------------------------------
st.markdown("""
<div class="hero">
    <h1>✉️ AI Email Generator</h1>
    <p>Create professional and personal emails in seconds.</p>
</div>
""", unsafe_allow_html=True)

st.write(
    "Describe what you want to say, choose your preferred tone, "
    "and let AI prepare an email for you."
)

# -----------------------------------
# 4. Read the API key securely
# -----------------------------------
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "Groq API key is missing. Add GROQ_API_KEY "
        "in your Streamlit app Secrets settings."
    )
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------------
# 5. Email input form
# -----------------------------------
with st.form("email_generator_form"):

    st.subheader("Email Details")

    col1, col2 = st.columns(2)

    with col1:
        email_type = st.selectbox(
            "Email Type",
            ["Professional", "Personal"]
        )

    with col2:
        tone = st.selectbox(
            "Writing Tone",
            [
                "Formal",
                "Friendly",
                "Polite",
                "Confident",
                "Apologetic",
                "Persuasive",
                "Warm and Appreciative"
            ]
        )

    recipient = st.text_input(
        "Recipient",
        placeholder="e.g. Hiring Manager, Teacher, Friend"
    )

    purpose = st.text_area(
        "Email Purpose *",
        placeholder=(
            "e.g. Write an email applying for a Python internship"
        ),
        height=100
    )

    details = st.text_area(
        "Additional Details (Optional)",
        placeholder=(
            "Add relevant names, dates, requests, "
            "or other information to include."
        ),
        height=120
    )

    length = st.selectbox(
        "Email Length",
        ["Short", "Medium", "Detailed"],
        index=1
    )

    submitted = st.form_submit_button(
        "✨ Generate Email"
    )

# -----------------------------------
# 6. Generate the email using Groq
# -----------------------------------
if submitted:

    if not purpose.strip():
        st.warning("Please enter the purpose of your email.")

    elif len(purpose) > 3000 or len(details) > 5000:
        st.warning(
            "Please shorten your purpose or additional details."
        )

    elif len(recipient) > 200:
        st.warning("Please shorten the recipient field.")

    else:
        prompt = f"""
You are an expert email-writing assistant.

Write an email using these requirements:

Email type: {email_type}
Recipient: {recipient.strip() or "Not specified"}
Purpose: {purpose.strip()}
Additional details: {details.strip() or "None provided"}
Tone: {tone}
Length: {length}

Instructions:
1. Generate a suitable subject line.
2. Include a greeting, clear body, and suitable closing.
3. Match the requested email type and tone.
4. Use only the information provided by the user.
5. Never invent qualifications, dates, events, or commitments.
6. Keep the email {length.lower()}.
7. Return the subject and email body only.

Use this format:

Subject: [Subject line]

[Greeting and email body]

[Closing]
"""

        try:
            with st.spinner(
                "Writing your email with AI... Please wait."
            ):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You write clear, natural, "
                                "well-organized emails. "
                                "Follow the user's requirements."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )

                generated_email = (
                    response.choices[0].message.content or ""
                ).strip()

            if not generated_email:
                st.error(
                    "The AI returned an empty response. Please try again."
                )
            else:
                st.session_state["generated_email"] = generated_email

        except Exception as error:
            # Keep private error details out of the public interface.
            print("Groq API error:", repr(error))
            st.error(
                "Sorry, email generation failed. Please check your "
                "API key, model availability, internet connection, "
                "and Groq usage limits, then try again."
            )

# -----------------------------------
# 7. Show and download the email
# -----------------------------------
if st.session_state.get("generated_email"):

    st.divider()
    st.subheader("Your Generated Email")

    generated_email = st.text_area(
        "Review or edit your email before sending",
        value=st.session_state["generated_email"],
        height=350,
        key="email_editor"
    )

    st.download_button(
        label="⬇️ Download Email (.txt)",
        data=generated_email,
        file_name="generated_email.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.caption(
        "Please review the email for accuracy before sending it."
    )

# -----------------------------------
# 8. Footer
# -----------------------------------
st.divider()

st.caption(
    "AI Email Generator | Powered by Streamlit and Groq"
)
