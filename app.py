import streamlit as st
import os
from datetime import datetime
import urllib.parse
import platform

# Set page config for a better look
st.set_page_config(page_title="Nested Folder & File Creator", page_icon="📁", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; padding: 20px; border-radius: 10px; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px 20px; }
    .stButton>button:hover { background-color: #45a049; }
    .stTextInput>div>div>input { border-radius: 5px; padding: 8px; }
    .stTextArea>div>div>textarea { border-radius: 5px; padding: 8px; }
    .status-box { padding: 15px; border-radius: 8px; margin-top: 10px; }
    .success { background-color: #d4edda; color: #155724; }
    .error { background-color: #f8d7da; color: #721c24; }
    .debug { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("📁 Nested Folder & File Creator")
st.markdown("Create a nested folder structure with custom text files and share the path for easy access!")

# Determine a safer default directory
user_home = os.path.expanduser("~")  # Gets C:\Users\valentina.akpan
default_base = os.path.join(user_home, "MyFolder")

# Input fields
base_dir = st.text_input("Base Directory", default_base, help="Where to create your structure, e.g., C:\\Users\\valentina.akpan\\MyFolder")
structure = st.text_area(
    "Folder Structure (one per line, use > for nesting)",
    "Project\nProject>Documents\nProject>Documents>Notes\nProject>Assets\nProject>Assets>Images",
    help="Define nested folders, e.g., 'Main>Sub>Deep' creates Main/Sub/Deep"
)
file_names = st.text_area(
    "Text Files (format: folder>file)",
    "Project>Documents>readme.txt\nProject>Documents>Notes>note1.txt\nProject>Assets>config.txt",
    help="List files with their folder path, e.g., 'Project>Documents>note.txt'"
)

# Advanced options
with st.expander("Advanced Options"):
    content = st.text_area("Default File Content", "This is a sample text file created on May 31, 2025.", help="Content for each new text file")
    overwrite = st.checkbox("Overwrite existing files/folders", value=False, help="If checked, overwrites existing items")
    debug_mode = st.checkbox("Enable Debug Info", value=True, help="Show detailed path and permission info")

# Button to create structure and files
if st.button("Create Structure & Files"):
    try:
        # Normalize and validate inputs
        base_dir = os.path.normpath(base_dir.strip())
        if not base_dir:
            raise ValueError("Base directory cannot be empty")
        
        # Create base directory if it doesn’t exist
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            if debug_mode:
                st.markdown("<div class='debug'>", unsafe_allow_html=True)
                st.write(f"Created base directory: {base_dir}")
                st.markdown("</div>", unsafe_allow_html=True)
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"Base directory '{base_dir}' could not be created or found")
        if not os.access(base_dir, os.W_OK):
            raise PermissionError(f"No write permission for '{base_dir}'")

        # Parse folder structure
        folder_list = [line.strip() for line in structure.split("\n") if line.strip()]
        created_folders = []
        created_files = []
        
        # Progress bar
        total_items = len(folder_list) + len([line for line in file_names.split("\n") if line.strip()])
        progress_bar = st.progress(0)
        progress = 0
        
        # Create nested folders
        for folder_path in folder_list:
            full_path = os.path.join(base_dir, folder_path.replace(">", os.sep))
            if debug_mode:
                st.markdown("<div class='debug'>", unsafe_allow_html=True)
                st.write(f"Attempting to create folder: {full_path}")
                st.write(f"Folder exists: {os.path.exists(full_path)}")
                st.write(f"Write permission: {os.access(base_dir, os.W_OK)}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if not os.path.exists(full_path) or overwrite:
                os.makedirs(full_path, exist_ok=True)
                created_folders.append(folder_path)
            progress += 1
            progress_bar.progress(min(progress / total_items, 1.0))
        
        # Verify folder creation
        missing_folders = [f for f in created_folders if not os.path.exists(os.path.join(base_dir, f.replace(">", os.sep)))]
        if missing_folders:
            raise RuntimeError(f"Failed to create folders: {', '.join(missing_folders)}")
        
        # Parse and create text files
        file_list = [line.strip() for line in file_names.split("\n") if line.strip()]
        for file_entry in file_list:
            if ">" not in file_entry:
                raise ValueError(f"Invalid file format: '{file_entry}'. Use 'folder>file'")
            parts = file_entry.rsplit(">", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid file entry: '{file_entry}'. Use 'folder>file'")
            folder_path, file_name = parts
            full_folder_path = os.path.join(base_dir, folder_path.replace(">", os.sep))
            full_file_path = os.path.join(full_folder_path, file_name)
            
            if debug_mode:
                st.markdown("<div class='debug'>", unsafe_allow_html=True)
                st.write(f"Attempting to create file: {full_file_path}")
                st.write(f"Folder exists: {os.path.exists(full_folder_path)}")
                st.write(f"File exists: {os.path.exists(full_file_path)}")
                st.write(f"Write permission for folder: {os.access(full_folder_path, os.W_OK) if os.path.exists(full_folder_path) else 'N/A'}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if not os.path.exists(full_folder_path):
                raise FileNotFoundError(f"Folder for file '{file_entry}' does not exist: {full_folder_path}")
            
            if not os.path.exists(full_file_path) or overwrite:
                with open(full_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                created_files.append(file_entry)
            progress += 1
            progress_bar.progress(min(progress / total_items, 1.0))
        
        # Verify created files
        missing_files = [f for f in created_files if not os.path.exists(os.path.join(base_dir, f.replace(">", os.sep)))]
        if missing_files:
            raise RuntimeError(f"Failed to create files: {', '.join(missing_files)}")
        
        # Scan base directory for actual contents
        actual_contents = []
        for root, dirs, files in os.walk(base_dir):
            rel_root = os.path.relpath(root, base_dir)
            for d in dirs:
                actual_contents.append(os.path.join(rel_root, d) if rel_root != "." else d)
            for f in files:
                actual_contents.append(os.path.join(rel_root, f) if rel_root != "." else f)
        
        # Generate file:// link for base directory
        file_url = f"file:///{urllib.parse.quote(base_dir.replace(os.sep, '/'))}"
        
        # Display success
        st.markdown(f"<div class='status-box success'>Success! Nested folders and files created!</div>", unsafe_allow_html=True)
        st.subheader("Created Items")
        st.write(f"**Base Folder**: {base_dir}")
        st.write("**Expected Folders**:")
        for folder in created_folders:
            st.write(f"✓ {folder}")
        st.write("**Expected Files**:")
        for file in created_files:
            st.write(f"✓ {file}")
        st.write("**Actual Contents in Structure**:")
        if actual_contents:
            for item in sorted(actual_contents):
                st.write(f"- {item}")
        else:
            st.write("Warning: Structure appears empty! Check permissions or path.")
        st.markdown(f"**Shareable Link**: <a href='{file_url}' target='_blank'>{file_url}</a>", unsafe_allow_html=True)
        st.write("**How to Check**: Open File Explorer, copy the base folder path above, paste it into the address bar, and press Enter.")
        st.write("Note: If the file:// link doesn’t work, manually navigate to the folder. For remote sharing, upload to a cloud service (e.g., Google Drive, Dropbox).")
        st.balloons()

    except Exception as e:
        # Display error
        st.markdown(f"<div class='status-box error'>An error occurred: {str(e)}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("**Note:** Use a safe directory like 'C:\\Users\\valentina.akpan\\MyFolder'. Run the terminal as administrator if blocked. Check 'Debug Info' for troubleshooting. Current time: 11:33 AM PDT, May 31, 2025.")
