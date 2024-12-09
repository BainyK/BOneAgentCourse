from openai import OpenAI
import streamlit as st
import time
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import tempfile
import os

client = OpenAI(base_url="http://localhost:11434/v1", api_key="not-needed")

# Inisialisasi text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Inisialisasi embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Tampilkan judul chatbot
st.title("Chatbot")

# Inisialisasi session state untuk vector store
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# Tambahkan area upload file PDF
uploaded_files = st.file_uploader("Upload file PDF", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    st.success(f"Berhasil mengupload {len(uploaded_files)} file")
    
    # Proses setiap file PDF
    documents = []
    for file in uploaded_files:
        # Simpan file sementara
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
            
        # Load dan proses PDF
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        documents.extend(pages)
        
        # Hapus file temporary
        os.unlink(tmp_path)
        
        st.write(f"Berhasil memproses: {file.name}")
    
    # Split dokumen menjadi chunks
    chunks = text_splitter.split_documents(documents)
    
    # Buat vector store
    st.session_state.vectorstore = FAISS.from_documents(chunks, embeddings)
    st.success("Dokumen berhasil diproses dan disimpan!")

# buat variable session
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Apa yang bisa saya bantu? Anda bisa bertanya tentang dokumen yang telah diupload."},
    ]

# Tampilkan History chat di box message
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Buat input box untuk menunggu chat dari user
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Cari konteks dari dokumen jika vectorstore tersedia
        context = ""
        if st.session_state.vectorstore is not None:
            results = st.session_state.vectorstore.similarity_search(prompt, k=3)
            context = "\n\n".join([doc.page_content for doc in results])
            
        # Buat prompt dengan konteks
        messages = [
            {"role": "system", "content": f"Anda adalah asisten yang membantu menjawab pertanyaan berdasarkan konteks berikut:\n\n{context}" if context else "Anda adalah asisten yang helpful."},
        ]
        messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])

        completion = client.chat.completions.create(
            model="llama3.2",
            messages=messages,
            stream=True,        
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content                  
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.03)
        
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})