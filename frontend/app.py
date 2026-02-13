import streamlit as st
import requests

st.set_page_config(page_title="CampusGenie", layout="centered")
st.title("CampusGenie: Chat with Campus PDFs")

role = st.selectbox("Role", ["Student", "Admin"])

if role == "Admin":
    st.header("Upload Document")
    doc_name = st.text_input("Document Name (e.g. syllabus.pdf)")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    if st.button("Upload") and uploaded_file and doc_name:
        files = {"file": uploaded_file.getvalue()}
        data = {"doc_name": doc_name}
        resp = requests.post("http://backend:8000/upload", files=files, data=data)
        st.success(f"Uploaded: {doc_name}")

st.header("Ask a Question")
question = st.text_input("Your question")
filter_docs = st.text_input("Filter by document (comma separated, optional)")
if st.button("Ask") and question:
    payload = {
        "question": question,
        "filter_docs": [d.strip() for d in filter_docs.split(",") if d.strip()] if filter_docs else None,
        "role": role,
        "history": None
    }
    resp = requests.post("http://backend:8000/chat", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        st.markdown(f"**Answer:** {data['answer']}")
        if data['citations']:
            st.markdown("**Citations:**")
            for cite in data['citations']:
                st.markdown(f"- {cite['doc']} page {cite['page']}\n> {cite['snippet'][:100]}...")
    else:
        st.error("Error: Could not get answer.")
