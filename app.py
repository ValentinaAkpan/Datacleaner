import streamlit as st
import os
from datetime import datetime
import shutil
import urllib.parse

# Set page config for a better look
st.set_page_config(page_title="Folder & Doc Creator", page_icon="📁", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; padding: 20px; border-radius: 10px; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px 20px; }
    .stButton>button:hover { background-color: #45a049; }
    .stTextInput>div>div>input { border-radius: 5px; padding: 8px; }
    .status-box { padding: 15px; border-radius: 8px; margin-top: 10px; }
    .success { background-color: #d4edda; color: #155724; }
    .error { background-color: #f8d7da; color: #721c24; }
    .debug { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("📁 Folder & Document Creator")
st.markdown("Create folders, add documents inside, and generate a file:// link to share your structure!")

# Input fields
base_dir = st.text_input("Base Directory", "C:/Users/YourName/Documents", help="Where to create your folders")
folder_name = st.text_input("Folder Name", "NewProject", help="Name of the new folder")
doc_names = st.text_area("Document Names (one per line)", "doc1.txt\ndoc2.txt\nreport.pdf", help="List documents to create, e.g., note.txt")

# Advanced options
with st.expander("Advanced Options"):
    content = st.text_area("Default Document Content", "This is a sample document created on May 31, 2025.", help="Content for each new document")
    overwrite = st.checkbox("Overwrite existing files", value=False, help="If checked, overwrites existing files/folders")
    debug_mode = st.checkbox("Enable Debug Info", value=False, help="Show detailed path and permission info")

# Button to create folders and documents
if st.button("Create & Generate Link"):
    try:
        # Normalize and validate base directory
        base_dir = os.path.normpath(base_dir.strip())
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"Base directory '{base_dir}' does not exist")
        if not os.access(base_dir, os.W_OK):
            raise PermissionError(f"No write permission for '{base_dir}'")

        # Create full path for the new folder
        new_folder_path = os.path.join(base_dir, folder_name.strip())
        
        # Debug info
        if debug_mode:
            st.markdown("<div class='debug'>", unsafe_allow_html=True)
            st.write(f"Attempting to create folder: {new_folder_path}")
            st.write(f"Base directory exists: {os.path.exists(base_dir)}")
            st.write(f"Write permission for base: {os.access(base_dir, os.W_OK)}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Check if folder exists and handle overwrite
        if os.path.exists(new_folder_path) and not overwrite:
            raise FileExistsError(f"Folder '{new_folder_path}' already exists! Check 'Overwrite' to replace.")
        
        # Create the folder
        os.makedirs(new_folder_path, exist_ok=True)
        
        # Parse document names from text area
        doc_list = [name.strip() for name in doc_names.split("\n") if name.strip()]
        created_files = []
        
        # Progress bar
        progress_bar = st.progress(0)
        total_items = len(doc_list) + 1  # +1 for folder creation
        progress = 0
        
        # Update progress for folder creation
        progress += 1
        progress_bar.progress(min(progress / total_items, 1.0))
        
        # Create documents inside the folder
        for doc in doc_list:
            doc_path = os.path.join(new_folder_path, doc)
            if debug_mode:
                st.markdown("<div class='debug'>", unsafe_allow_html=True)
                st.write(f"Attempting to create file: {doc_path}")
                st.write(f"File exists: {os.path.exists(doc_path)}")
                st.write(f"Write permission for folder: {os.access(new_folder_path, os.W_OK)}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if not os.path.exists(doc_path) or overwrite:
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(doc)
            progress += 1
            progress_bar.progress(min(progress / total_items, 1.0))
        
        # Generate file:// link
        file_url = f"file://{urllib.parse.quote(new_folder_path.replace(os.sep, '/'))}"
        
        # Display success
        st.markdown(f"<div class='status-box success'>Success! Folder and documents created!</div>", unsafe_allow_html=True)
        st.subheader("Created Items")
        st.write(f"**Folder**: {new_folder_path}")
        st.write("**Documents**:")
        for file in created_files:
            st.write(f"✓ {file}")
        st.markdown(f"**Shareable Link**: <a href='{file_url}' target='_blank'>{file_url}</a>", unsafe_allow_html=True)
        st.write("Note: The file:// link works locally. For remote sharing, upload to a cloud service (e.g., Google Drive, Dropbox).")
        st.balloons()

    except Exception as e:
        # Display error
        st.markdown(f"<div class='status-box error'>An error occurred: {str(e)}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("**Note:** Ensure the base directory exists and you have write permissions. Check 'Debug Info' for troubleshooting.")
