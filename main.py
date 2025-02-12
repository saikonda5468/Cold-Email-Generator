import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import validators

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.danaher.com/global/en/search-results")
    submit_button = st.button("Submit")
    
    if submit_button:
        try:
            if not validators.url(url_input):
                st.error("Invalid URL. Please enter a valid link.")
                return

            loader = WebBaseLoader([url_input])
            raw_content = loader.load()
            if not raw_content:
                st.error("No content retrieved from the URL.")
                return
            
            data = clean_text(raw_content.pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            print(jobs)
            if not jobs:
                st.error("No jobs found in the content.")
                return

            for job in jobs[0:3]:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links) 
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")
            st.write("Please check the URL or try a different one.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)