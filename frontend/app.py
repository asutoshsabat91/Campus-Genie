import streamlit as st
import requests

st.set_page_config(page_title="CampusGenie", layout="wide")
st.title("CampusGenie: Chat with Campus PDFs")

# Sidebar for navigation and document management
st.sidebar.header("CampusGenie Controls")
role = st.sidebar.selectbox("Role", ["Student", "Admin"])

# Show uploaded documents
st.sidebar.subheader("Uploaded Documents")
try:
    docs_resp = requests.get("http://backend:8000/docs")
    docs = docs_resp.json()["docs"] if docs_resp.status_code == 200 else []
except:
    docs = []
if docs:
    st.sidebar.write("\n".join([f"- {d}" for d in docs]))
else:
    st.sidebar.write("No documents uploaded yet.")

# Document filter
filter_docs = st.sidebar.multiselect("Filter by document", docs)

# Main area
if role == "Admin":
    st.header("Upload Document")
    doc_name = st.text_input("Document Name (e.g. syllabus.pdf)")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
    if st.button("Upload") and uploaded_file and doc_name:
        files = {"file": uploaded_file.getvalue()}
        data = {"doc_name": doc_name}
        resp = requests.post("http://backend:8000/upload", files=files, data=data)
        if resp.status_code == 200:
            st.success(f"Uploaded: {doc_name}")
        else:
            st.error("Upload failed.")

st.header("Chat with CampusGenie")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

question = st.text_input("Your question")
if st.button("Ask") and question:
    payload = {
        "question": question,
        "filter_docs": filter_docs if filter_docs else None,
        "role": role,
        "history": st.session_state["chat_history"]
    }
    resp = requests.post("http://backend:8000/chat", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        st.session_state["chat_history"].append({"question": question, "answer": data["answer"], "citations": data["citations"]})
        st.markdown(f"**Answer:** {data['answer']}")
        if data['citations']:
            st.markdown("**Citations:**")
            for cite in data['citations']:
                st.markdown(f"- **{cite['doc']}** page {cite['page']}<br><span style='font-size:small'>{cite['snippet'][:120]}...</span>", unsafe_allow_html=True)
    else:
        st.error("Error: Could not get answer.")

# Show chat history
st.subheader("Chat History")
for entry in st.session_state["chat_history"][::-1]:
    st.markdown(f"**Q:** {entry['question']}")
    st.markdown(f"**A:** {entry['answer']}")
    if entry['citations']:
        for cite in entry['citations']:
            st.markdown(f"<span style='font-size:small'>- {cite['doc']} page {cite['page']}<br>{cite['snippet'][:120]}...</span>", unsafe_allow_html=True)
    st.markdown("---")
