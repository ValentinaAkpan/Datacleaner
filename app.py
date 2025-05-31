import streamlit as st
import pandas as pd
import io
import os

# Set page config
st.set_page_config(page_title="Data Cleaner", page_icon="🧹", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7fa; padding: 20px; border-radius: 10px; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px 20px; }
    .stButton>button:hover { background-color: #45a049; }
    .stFileUploader>div>div>input { border-radius: 5px; padding: 8px; }
    .stSelectbox>div>div>select { border-radius: 5px; padding: 8px; }
    .stNumberInput>div>div>input { border-radius: 5px; padding: 8px; }
    .status-box { padding: 15px; border-radius: 8px; margin-top: 10px; }
    .success { background-color: #d4edda; color: #155724; }
    .error { background-color: #f8d7da; color: #721c24; }
    .debug { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("🧹 Data Cleaner")
st.markdown("Upload a CSV file, clean it (remove duplicates, handle missing values), and download the result!")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"], help="Upload a CSV to clean")

# Initialize session state for data
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.cleaned_df = None

# Process uploaded file
if uploaded_file:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.cleaned_df = st.session_state.df.copy()
        st.markdown("<div class='status-box success'>File uploaded successfully!</div>", unsafe_allow_html=True)
        st.subheader("Original Data Preview")
        st.dataframe(st.session_state.df.head())
        st.write(f"Rows: {st.session_state.df.shape[0]}, Columns: {st.session_state.df.shape[1]}")
    except Exception as e:
        st.markdown(f"<div class='status-box error'>Error loading file: {str(e)}</div>", unsafe_allow_html=True)

# Cleaning options
if st.session_state.df is not None:
    st.subheader("Cleaning Options")
    
    with st.expander("Cleaning Settings"):
        remove_duplicates = st.checkbox("Remove Duplicates", value=True, help="Remove duplicate rows")
        fill_method = st.selectbox(
            "Handle Missing Values",
            ["None", "Fill with 0", "Fill with Mean", "Fill with Median", "Drop Rows"],
            help="Choose how to handle missing (NaN) values"
        )
        debug_mode = st.checkbox("Enable Debug Info", value=True, help="Show data stats and changes")

    # Button to clean data
    if st.button("Clean Data"):
        try:
            cleaned_df = st.session_state.df.copy()
            
            # Remove duplicates
            if remove_duplicates:
                initial_rows = cleaned_df.shape[0]
                cleaned_df = cleaned_df.drop_duplicates()
                removed = initial_rows - cleaned_df.shape[0]
                if debug_mode:
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write(f"Duplicates removed: {removed} rows")
                    st.markdown("</div>", unsafe_allow_html=True)

            # Handle missing values
            if fill_method != "None":
                if debug_mode:
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write("Missing values before cleaning:")
                    st.write(cleaned_df.isnull().sum())
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if fill_method == "Fill with 0":
                    cleaned_df = cleaned_df.fillna(0)
                elif fill_method == "Fill with Mean":
                    for col in cleaned_df.select_dtypes(include=['float', 'int']).columns:
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
                elif fill_method == "Fill with Median":
                    for col in cleaned_df.select_dtypes(include=['float', 'int']).columns:
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                elif fill_method == "Drop Rows":
                    initial_rows = cleaned_df.shape[0]
                    cleaned_df = cleaned_df.dropna()
                    removed = initial_rows - cleaned_df.shape[0]
                    if debug_mode:
                        st.markdown("<div class='debug'>", unsafe_allow_html=True)
                        st.write(f"Rows dropped due to missing values: {removed}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                if debug_mode:
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write("Missing values after cleaning:")
                    st.write(cleaned_df.isnull().sum())
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Store cleaned data
            st.session_state.cleaned_df = cleaned_df
            
            # Display results
            st.markdown("<div class='status-box success'>Data cleaned successfully!</div>", unsafe_allow_html=True)
            st.subheader("Cleaned Data Preview")
            st.dataframe(st.session_state.cleaned_df.head())
            st.write(f"Rows: {st.session_state.cleaned_df.shape[0]}, Columns: {st.session_state.cleaned_df.shape[1]}")
            
            # Download cleaned data
            csv = st.session_state.cleaned_df.to_csv(index=False)
            st.download_button(
                label="Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv",
                help="Download the cleaned data as a CSV file"
            )
            st.balloons()
        
        except Exception as e:
            st.markdown(f"<div class='status-box error'>Error cleaning data: {str(e)}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("**Note:** Upload a CSV file to start. Use cleaning options to remove duplicates or handle missing values. Current time: 11:36 AM PDT, May 31, 2025.")
