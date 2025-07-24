import os 
import requests

def call_mistral_api(api_key, prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
            
        elif response.status_code == 429:
            wait = 2 ** 3
            print(f"⏳ 429 Too Many Requests - retrying in {wait}s...")
            time.sleep(wait)
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error {response.status_code}: {response.text}"}

        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def create_ats_generated_resume(my_resume,job_description):
    # Get your Groq API key from the environment variable 
    api_key = "oGGtDcv5ECoaWSvDVIlfvDUwF5rx7rKc"


    # --- THE PROMPT FOR THE GROQ MODEL --- 
    prompt = f"""
            Below is my resume:\n\n{my_resume}\n\n
            Job Description:\n\n{job_description}\n\n
            Please create my Resume according to this Job Description. Also add my skills according to JD, write exact term used in JD. Try to create best Resume with Best ATS Score
            """
    

    try: 
        response = call_mistral_api(api_key, prompt)
        content = response["choices"][0]["message"]["content"]

        return content

    except Exception as e: 
        print(f"An error occurred: {e}") 
        return ""