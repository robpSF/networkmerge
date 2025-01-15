import streamlit as st
import pandas as pd
import numpy as np

def merge_networks(file1, file2):
    # Read the input Excel files
    df1 = pd.read_excel(file1, header=2)  # Start reading from row 3
    df2 = pd.read_excel(file2, header=2)
    st.write(df1)
    st.write(df2)

    # Get the full set of personas from both files
    all_personas = sorted(set(df1.iloc[:, 0]) | set(df2.iloc[:, 0]))

    # Align columns to ensure both dataframes have the same columns
    all_columns = sorted(set(df1.columns) | set(df2.columns))
    df1 = df1.reindex(columns=all_columns, fill_value=np.nan)
    df2 = df2.reindex(columns=all_columns, fill_value=np.nan)


    # Initialize the merged DataFrame
    merged_df = pd.DataFrame(index=all_personas, columns=all_columns)
    merged_df.iloc[:, 0] = all_personas  # Populate the Persona column

    # Define merge logic
    def resolve_conflict(val1, val2):
        if pd.isna(val1):
            return val2
        if pd.isna(val2):
            return val1
        if val1 == val2:
            return val1
        if val1 == 2 or val2 == 2:
            return 2
        if {val1, val2} == {1, 3}:
            return 2
        return max(val1, val2)  # Fallback

    # Merge the data
    for col in all_columns[4:]:  # Skip columns A-D
        merged_df[col] = [
            resolve_conflict(df1.at[row, col], df2.at[row, col])
            for row in all_personas
        ]

    # Fill blank cells with 0 (optional; adjust if necessary)
    merged_df = merged_df.fillna(0)
    return merged_df

def main():
    st.title("Network Merger")
    st.write("Upload two Excel files to merge their network diagrams.")

    # File upload inputs
    file1 = st.file_uploader("Upload the first network file", type="xlsx")
    file2 = st.file_uploader("Upload the second network file", type="xlsx")

    if file1 and file2:
        with st.spinner("Merging networks..."):
            merged_network = merge_networks(file1, file2)

        st.success("Networks merged successfully!")

        # Provide the merged file for download
        st.write("Download the merged network:")
        merged_file = merged_network.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="Download Merged Network",
            data=merged_file,
            file_name="merged_network.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
