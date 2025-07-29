# app.py

import streamlit as st
import os
import json
from groq import Groq
from dotenv import load_dotenv

from file_parser import read_uploaded_file
from pdf_generator import create_beautiful_pdf
from create_ats_resume import create_ats_generated_resume
# --- PAGE CONFIGURATION & API KEY SETUP ---
st.set_page_config(page_title="AI Professional CV Generator", page_icon="📄", layout="wide")

# --- SECURE API KEY LOADING ---
load_dotenv()
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.secrets["GROQ_API_KEY"]
    api_key = "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"
    client = Groq(api_key=api_key)
except Exception:
    st.error("Groq API Key not found. Please set it in your .env file or Streamlit secrets.")
    st.stop()


# --- AI FUNCTIONS ---

def parse_resume_with_ai(resume_text, job_description = None):
    """Parses resume text into a structured JSON, now with skills as a list."""
    # (The AI parsing prompt is updated for better skill and education parsing)
    if job_description:
        resume_text_ats = create_ats_generated_resume(resume_text,job_description)
        if resume_text_ats != "":
            resume_text = resume_text_ats    
        

    prompt = f"""
    You are a world-class resume parsing AI. Convert the resume text into a structured JSON object.
    
    **JSON Structure:**
    {{
    "personal_info": {{ "name": "...", "email": "...", "phone": "...", "linkedin": "..." }},
    "summary": "...",
    "experience": [ {{"title": "...", "company": "...", "dates": "...", "description": "..."}} ],
    "projects": [ {{"title": "...", "dates": "...", "description": "..."}} ],
    "achievements": [ {{"description": "..."}} ],
    "education": [ {{"degree": "Degree Name", "institution_dates": "Institution | Dates"}} ],
    "skills": ["Skill 1", "Skill 2", "Skill 3"]
    }}

    **Resume Text to Parse:** --- {resume_text} ---
    """
        

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a resume parsing expert that only outputs valid JSON."}, {"role": "user", "content": prompt}],
            model="llama3-70b-8192", temperature=0.1, response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        st.error(f"AI parsing failed: {e}")
        return None

def refine_text_with_ai(original_text, context):
    """Generic AI function to refine text, now with achievements context."""
    prompts = {
        "summary": "Rewrite the following professional summary to be more impactful in 50-60 words for a CV.",
        "experience": "Rewrite the following job responsibilities into 4-5 concise points, action-oriented bullet points for a CV. Use strong action verbs (e.g., 'Engineered', 'Led') and focus on quantifiable achievements. Start each point with '•'.",
        "project": "Rewrite the following project description in bullet points. Focus on the technologies used and the outcome. Start each point with '•'.",
        "achievement": "Rewrite the following achievement to be more impactful and professional for a CV. Use the STAR method (Situation, Task, Action, Result) if applicable, but keep it concise (1-2 sentences)."
    }
    prompt = f"{prompts.get(context, 'Rewrite the following text:')}\n\n--- TEXT ---\n{original_text}"
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-70b-8192", temperature=0.6
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"AI refinement failed: {e}")
        return original_text

def suggest_skills_with_ai(job_title):
    """NEW: Suggests skills based on a job title."""
    prompt = f"Based on the job title '{job_title}', generate a list of 10-15 relevant technical and soft skills for a resume. Output ONLY a single comma-separated string of these skills and nothing else."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", temperature=0.5
        )
        skills_str = chat_completion.choices[0].message.content.strip()
        return [skill.strip() for skill in skills_str.split(',') if skill.strip()]
    except Exception as e:
        st.error(f"AI skill suggestion failed: {e}")
        return []


# --- INITIALIZE SESSION STATE ---
if 'cv_data' not in st.session_state:
    st.session_state.cv_data = {
        "personal_info": {}, "summary": "", "experience": [], "projects": [],
        "achievements": [], "education": [], "skills": []
    }
if 'suggested_skills' not in st.session_state:
    st.session_state.suggested_skills = []

# --- UI: HEADER AND UPLOAD ---
st.title("📄✨ AI Professional CV Generator")
st.markdown("Create a polished, modern CV. Upload your resume to auto-fill, or build it from scratch with our dynamic editor.")
# --- New Block: Job Description Input ---

job_description = None  # Default value

with st.expander("📋 Paste Job Description (Optional)"):
    jd_input = st.text_area("Paste the job description here to tailor your CV for better ATS scores:", height=200)
    if jd_input.strip():
        job_description = jd_input.strip()

with st.expander("📂 Upload Your Resume to Start (Recommended)"):
    # ... (Upload logic is the same, no changes needed)
    uploaded_file = st.file_uploader("Upload a PDF or Word document.", type=["pdf", "docx"], label_visibility="collapsed")
    if uploaded_file and st.button("🚀 Analyze Resume with AI"):
        with st.spinner("Reading file..."):
            raw_text = read_uploaded_file(uploaded_file)
        if raw_text:
            with st.spinner("AI is analyzing your resume..."):
                parsed_data = parse_resume_with_ai(raw_text, job_description)
                if parsed_data:
                    for key, value in parsed_data.items():
                        if value or (isinstance(value, list) and len(value) > 0):
                            st.session_state.cv_data[key] = value
                    st.success("✅ AI analysis complete! The form is now pre-filled.")

# --- UI: DYNAMIC FORM ---
st.header("📝 Review and Refine Your CV Details")
data = st.session_state.cv_data

def create_delete_button(collection, index, type_name):
    if st.button(f"🗑️ Delete", key=f"delete_{type_name}_{index}", help=f"Delete this {type_name} entry"):
        del collection[index]
        st.rerun()

# --- FORM SECTIONS ---
with st.container(border=True):
    st.subheader("Personal Information")
    # ... (This section is the same, no changes needed)
    pi = data.setdefault('personal_info', {})
    col1, col2 = st.columns(2)
    pi['name'] = col1.text_input("Full Name", pi.get('name', ''))
    pi['email'] = col2.text_input("Email", pi.get('email', ''))
    pi['phone'] = col1.text_input("Phone", pi.get('phone', ''))
    pi['linkedin'] = col2.text_input("LinkedIn URL", pi.get('linkedin', ''))

with st.container(border=True):
    st.subheader("Professional Summary")
    # ... (This section is the same, no changes needed)
    data['summary'] = st.text_area("Summary", data.get('summary', ''), height=150, label_visibility="collapsed")
    if st.button("✨ Refine Summary with AI"):
        with st.spinner("AI is crafting a new summary..."):
            data['summary'] = refine_text_with_ai(data['summary'], "summary")
        st.rerun()

# --- DYNAMIC LISTS WITH DELETE FUNCTIONALITY ---
# Each section is now wrapped in a container for better visual separation.
# The `create_delete_button` helper is used in each loop.

# Work Experience
with st.container(border=True):
    st.subheader("Work Experience")
    for i, job in enumerate(data.setdefault('experience', [])):
        with st.container(border=True):
            cols = st.columns([0.8, 0.2])
            cols[1].markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Spacer for alignment
            with cols[1]:
                create_delete_button(data['experience'], i, "Job")
            # ... (rest of the job entry UI is the same)
            job['title'] = st.text_input("Job Title", job.get('title', ''), key=f"exp_title_{i}")
            col1, col2 = st.columns([3, 1])
            job['company'] = col1.text_input("Company", job.get('company', ''), key=f"exp_company_{i}")
            job['dates'] = col2.text_input("Dates", job.get('dates', ''), key=f"exp_dates_{i}")
            job['description'] = st.text_area("Description", job.get('description', ''), height=150, key=f"exp_desc_{i}")
            if st.button("✨ Refine Description", key=f"refine_exp_{i}"):
                with st.spinner("AI is refining..."):
                    job['description'] = refine_text_with_ai(job['description'], "experience")
                st.rerun()
    if st.button("Add Job", use_container_width=True):
        data['experience'].append({})
        st.rerun()

# Projects
with st.container(border=True):
    st.subheader("Projects")
    # ... (Project section follows the same pattern as Work Experience)
    for i, proj in enumerate(data.setdefault('projects', [])):
        with st.container(border=True):
            cols = st.columns([0.8, 0.2])
            with cols[1]:
                create_delete_button(data['projects'], i, "Project")
            proj['title'] = st.text_input("Project Title", proj.get('title', ''), key=f"proj_title_{i}")
            proj['description'] = st.text_area("Description", proj.get('description', ''), height=120, key=f"proj_desc_{i}")
            if st.button("✨ Refine Description", key=f"refine_proj_{i}"):
                with st.spinner("AI is refining..."):
                    proj['description'] = refine_text_with_ai(proj['description'], "project")
                st.rerun()
    if st.button("Add Project", use_container_width=True):
        data['projects'].append({})
        st.rerun()

# Achievements
with st.container(border=True):
    st.subheader("Achievements (Optional)")
    for i, ach in enumerate(data.setdefault('achievements', [])):
        with st.container(border=True):
            cols = st.columns([0.8, 0.2])
            with cols[1]:
                create_delete_button(data['achievements'], i, "Achievement")
            ach['description'] = st.text_area("Achievement", ach.get('description', ''), height=80, key=f"ach_desc_{i}")
            # NEW: AI for achievements
            if st.button("✨ Refine Achievement", key=f"refine_ach_{i}"):
                with st.spinner("AI is refining..."):
                    ach['description'] = refine_text_with_ai(ach['description'], "achievement")
                st.rerun()
    if st.button("Add Achievement", use_container_width=True):
        data['achievements'].append({})
        st.rerun()

# Education
with st.container(border=True):
    st.subheader("Education")
    for i, edu in enumerate(data.setdefault('education', [])):
        with st.container(border=True):
            cols = st.columns([0.8, 0.2])
            with cols[1]:
                create_delete_button(data['education'], i, "Education")
            edu['degree'] = st.text_input("Degree", edu.get('degree', ''), key=f"edu_degree_{i}")
            edu['institution_dates'] = st.text_input("Institution | Dates", edu.get('institution_dates', ''), key=f"edu_inst_{i}")
    if st.button("Add Education", use_container_width=True):
        data['education'].append({})
        st.rerun()

# Skills
with st.container(border=True):
    st.subheader("Skills")
    st.markdown("**Your Current Skills:**")
    # FIX: Correctly display and delete skills
    if not data.setdefault('skills', []):
        st.caption("No skills added yet.")
    
    num_cols = 4 # Display skills in 4 columns
    cols = st.columns(num_cols)
    for i, skill in enumerate(data['skills']):
        with cols[i % num_cols]:
            if st.button(f"🗑️ {skill}", key=f"delete_skill_{i}", help="Delete skill", use_container_width=True):
                del data['skills'][i]
                st.rerun()

    st.markdown("---")
    st.markdown("**Add a New Skill:**")
    new_skill = st.text_input("New Skill", key="new_skill_input", label_visibility="collapsed")
    if st.button("Add Skill", use_container_width=True):
        if new_skill and new_skill not in data['skills']:
            data['skills'].append(new_skill)
            st.rerun()
    
    st.markdown("---")
    st.markdown("**Get AI Skill Suggestions:**")
    suggestion_role = st.text_input("Enter a job title to get suggestions", "e.g., Data Scientist")
    if st.button("Get Suggestions"):
        with st.spinner("AI is thinking of relevant skills..."):
            st.session_state.suggested_skills = suggest_skills_with_ai(suggestion_role)

    if st.session_state.suggested_skills:
        st.markdown("**Click a skill to add it to your list:**")
        cols = st.columns(4)
        for i, skill in enumerate(st.session_state.suggested_skills):
            with cols[i % num_cols]:
                if st.button(skill, key=f"suggest_skill_{i}", use_container_width=True):
                    if skill not in data['skills']:
                        data['skills'].append(skill)
                    st.session_state.suggested_skills.remove(skill)
                    st.rerun()

def generate_cover_letter(resume_text, job_description):
    """Generates a cover letter using the Groq API, given resume text and job description."""
    prompt = f"""
    You are an expert cover letter writer. Based on the following resume and job description, write a compelling cover letter.

    **Resume:**
    {resume_text}

    **Job Description:**
    {job_description}

    **Instructions:**
    - Focus on how the candidate's skills and experience align with the job requirements.
    - Use a professional and enthusiastic tone.
    - Keep the cover letter concise and to the point (around 300-400 words).
    - Include a strong call to action, inviting the hiring manager to contact the candidate.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.7
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Cover letter generation failed: {e}")
        return None


# --- FINAL GENERATION BUTTON ---
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Generate Final PDF", type="primary", use_container_width=True):
        # ... (This logic is the same, no changes needed)
        with st.spinner("Creating your beautiful CV..."):
            try:
                pdf_bytes = create_beautiful_pdf(st.session_state.cv_data)
                st.download_button(
                    label="📥 Download Your Professional CV",
                    data=pdf_bytes,
                    file_name=f"{data['personal_info'].get('name', 'CV').replace(' ', '_')}_CV.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

with col2:
    if job_description:
        if st.button("✍️ Generate Cover Letter", use_container_width=True):
            with st.spinner("Generating your cover letter..."):
                # Extract resume text from the session state
                resume_text = ""
                if st.session_state.cv_data:
                    # You might need to adjust this part depending on how your resume data is structured
                    resume_text = f"""
                    Personal Info: {st.session_state.cv_data.get('personal_info', {})}
                    Summary: {st.session_state.cv_data.get('summary', '')}
                    Experience: {st.session_state.cv_data.get('experience', [])}
                    Projects: {st.session_state.cv_data.get('projects', [])}
                    Achievements: {st.session_state.cv_data.get('achievements', [])}
                    Education: {st.session_state.cv_data.get('education', [])}
                    Skills: {st.session_state.cv_data.get('skills', [])}
                    """  # Construct resume text
                cover_letter = generate_cover_letter(resume_text, job_description)
                if cover_letter:
                    st.text_area("Cover Letter", value=cover_letter, height=300)
                    st.download_button(
                        label="📥 Download Cover Letter",
                        data=cover_letter.encode(),
                        file_name=f"{data['personal_info'].get('name', 'Cover_Letter').replace(' ', '_')}_Cover_Letter.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate cover letter.")