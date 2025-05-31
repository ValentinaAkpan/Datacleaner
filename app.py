import streamlit as st
import pandas as pd
import io
import os

# Set up the app's look
st.set_page_config(page_title="Data Cleaner", page_icon="🧹", layout="wide")

# Style the app to make it pretty
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
    .explain { background-color: #e9f5ff; color: #1c2526; padding: 10px; border-radius: 5px; }
    .warning { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Title and intro
st.title("Data Cleaner")
st.markdown("**Welcome!** Upload a CSV file (like a spreadsheet), and I’ll help clean it up by fixing duplicates and missing values. You can then download the tidy version!")



# File uploader
uploaded_file = st.file_uploader("Step 1: Upload Your CSV File", type=["csv"], help="Pick a CSV file from your computer to clean")

# Store data in memory
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.cleaned_df = None

# Process the uploaded file
if uploaded_file:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.cleaned_df = st.session_state.df.copy()
        st.markdown("<div class='status-box success'>Yay! File uploaded successfully!</div>", unsafe_allow_html=True)
        st.subheader("Preview of Your Original Data")
        st.markdown("<div class='explain'>", unsafe_allow_html=True)
        st.write("**What’s Happening?** I loaded your file and I’m showing the first few rows below. ‘Rows’ are the number of entries, and ‘Columns’ are the fields (like ‘Name’ or ‘Price’).")
        st.markdown("</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.df.head())
        st.write(f"Rows: {st.session_state.df.shape[0]} (entries), Columns: {st.session_state.df.shape[1]} (fields)")
        st.markdown("<div class='explain'>", unsafe_allow_html=True)
        st.write("**Check for Blanks**: Here’s where your data has missing values (blank spots) before cleaning:")
        st.markdown("</div>", unsafe_allow_html=True)
        st.dataframe(st.session_state.df[st.session_state.df.isnull().any(axis=1)].head())
        st.write(f"Rows with at least one blank: {st.session_state.df.isnull().any(axis=1).sum()}")
    except Exception as e:
        st.markdown(f"<div class='status-box error'>Oops! Couldn’t load the file: {str(e)}</div>", unsafe_allow_html=True)

# Cleaning options
if st.session_state.df is not None:
    st.subheader("Step 2: Choose How to Clean Your Data")
    st.markdown("<div class='explain'>", unsafe_allow_html=True)
    st.write("**What’s Cleaning?** Your data might have issues: duplicate rows (same entry twice) or missing values (blank spots). Pick options below to fix these!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.expander("Cleaning Settings"):
        remove_duplicates = st.checkbox(
            "Remove Duplicates", value=True, 
            help="If checked, I’ll delete any repeat rows (e.g., if ‘May 31, 2025, $50, Shoes’ appears twice, I keep one)"
        )
        fill_method = st.selectbox(
            "Handle Missing Values",
            ["None", "Fill with 0", "Fill with Mean", "Fill with Median", "Drop Rows"],
            help="Missing values are blank spots. Choose: do nothing, fill with 0, use the average, use the middle value, or remove rows with blanks"
        )
        debug_mode = st.checkbox(
            "Show Me the Details", value=True, 
            help="Check this to see extra info, like how many duplicates I found or how many blanks were fixed"
        )
        drop_proceed = st.checkbox(
            "Proceed if Dropping Rows Empties Data", value=False,
            help="If ‘Drop Rows’ removes all rows (e.g., every row has a blank), check this to continue anyway"
        )

    # Button to clean data
    if st.button("Step 3: Clean My Data!"):
        try:
            cleaned_df = st.session_state.df.copy()
            
            # Remove duplicates
            if remove_duplicates:
                initial_rows = cleaned_df.shape[0]
                cleaned_df = cleaned_df.drop_duplicates()
                removed = initial_rows - cleaned_df.shape[0]
                st.markdown("<div class='explain'>", unsafe_allow_html=True)
                st.write(f"**What I Did: Removed Duplicates** I checked for rows that are exactly the same and removed {removed} duplicates. For example, if ‘May 31, 2025, $50, Shoes’ was there twice, I kept one.")
                st.markdown("</div>", unsafe_allow_html=True)
                if debug_mode:
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write(f"Duplicates removed: {removed} rows")
                    st.markdown("</div>", unsafe_allow_html=True)

            # Handle missing values
            if fill_method != "None":
                st.markdown("<div class='explain'>", unsafe_allow_html=True)
                st.write("**What I Did: Fixed Missing Values** I found blank spots (called ‘NaN’) in your data. Here’s how I handled them based on your choice:")
                st.markdown("</div>", unsafe_allow_html=True)
                if debug_mode:
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write("Missing values before cleaning (blanks per column):")
                    st.write(cleaned_df.isnull().sum())
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if fill_method == "Fill with 0":
                    cleaned_df = cleaned_df.fillna(0)
                    st.markdown("<div class='explain'>", unsafe_allow_html=True)
                    st.write("**Choice: Fill with 0** I put a 0 in every blank spot. Good for numbers like sales or counts!")
                    st.markdown("</div>", unsafe_allow_html=True)
                elif fill_method == "Fill with Mean":
                    for col in cleaned_df.select_dtypes(include=['float', 'int']).columns:
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
                    st.markdown("<div class='explain'>", unsafe_allow_html=True)
                    st.write("**Choice: Fill with Mean** For number columns, I calculated the average (e.g., for ‘Amount’ with 10, 20, blank, 30, the mean is 20) and filled blanks with that.")
                    st.markdown("</div>", unsafe_allow_html=True)
                elif fill_method == "Fill with Median":
                    for col in cleaned_df.select_dtypes(include=['float', 'int']).columns:
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                    st.markdown("<div class='explain'>", unsafe_allow_html=True)
                    st.write("**Choice: Fill with Median** For number columns, I found the middle value (e.g., for 10, 20, 30, the median is 20) and filled blanks with that. Great if you have extreme values!")
                    st.markdown("</div>", unsafe_allow_html=True)
                elif fill_method == "Drop Rows":
                    initial_rows = cleaned_df.shape[0]
                    rows_to_drop = cleaned_df.isnull().any(axis=1).sum()
                    if rows_to_drop == initial_rows and not drop_proceed:
                        st.markdown("<div class='warning'>", unsafe_allow_html=True)
                        st.write(f"**Warning!** I found {rows_to_drop} rows with blanks. Dropping them would leave NO data! Check ‘Proceed if Dropping Rows Empties Data’ to continue, or pick another option like ‘Fill with 0’.")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        cleaned_df = cleaned_df.dropna()
                        removed = initial_rows - cleaned_df.shape[0]
                        st.markdown("<div class='explain'>", unsafe_allow_html=True)
                        st.write(f"**Choice: Drop Rows** I removed {removed} rows that had any blank values. This keeps only complete data! If the result is empty, it means every row had a blank.")
                        st.markdown("</div>", unsafe_allow_html=True)
                        if debug_mode:
                            st.markdown("<div class='debug'>", unsafe_allow_html=True)
                            st.write(f"Rows dropped due to missing values: {removed}")
                            st.markdown("</div>", unsafe_allow_html=True)
                
                if debug_mode and fill_method != "Drop Rows" or (fill_method == "Drop Rows" and (drop_proceed or rows_to_drop < initial_rows)):
                    st.markdown("<div class='debug'>", unsafe_allow_html=True)
                    st.write("Missing values after cleaning (blanks per column):")
                    st.write(cleaned_df.isnull().sum())
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Store cleaned data
            st.session_state.cleaned_df = cleaned_df
            
            # Display results
            st.markdown("<div class='status-box success'>Woohoo! Data cleaned successfully!</div>", unsafe_allow_html=True)
            st.subheader("Step 4: See Your Cleaned Data")
            st.markdown("<div class='explain'>", unsafe_allow_html=True)
            st.write("**What’s Happening?** Below is a preview of your cleaned data (first few rows). I also show the new number of rows and columns. Check it out!")
            st.markdown("</div>", unsafe_allow_html=True)
            st.dataframe(st.session_state.cleaned_df.head())
            st.write(f"Rows: {st.session_state.cleaned_df.shape[0]} (entries), Columns: {st.session_state.cleaned_df.shape[1]} (fields)")
            
            # Download cleaned data
            st.subheader("Step 5: Download Your Cleaned Data")
            st.markdown("<div class='explain'>", unsafe_allow_html=True)
            st.write("**What’s Happening?** Click the button below to save your cleaned data as a new CSV file (‘cleaned_data.csv’) to your computer. You can open it in Excel or use it elsewhere!")
            st.markdown("</div>", unsafe_allow_html=True)
            csv = st.session_state.cleaned_df.to_csv(index=False)
            st.download_button(
                label="Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv",
                help="Click to save your cleaned data as a CSV file"
            )
            st.balloons()
        
        except Exception as e:
            st.markdown(f"<div class='status-box error'>Oops! Error cleaning data: {str(e)}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("**Note:** Start by uploading a CSV file. Pick cleaning options to fix duplicates or missing values. Watch for warnings if dropping rows empties your data! Current time: 11:46 AM PDT, May 31, 2025.")
