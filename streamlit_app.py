import streamlit as st
import pandas as pd
from io import BytesIO

# Streamlit app
st.title("Social Network Merger")

st.markdown("Upload two Excel files containing directed social networks to merge them into a single dataframe.")

# Upload first Excel file
st.header("Step 1: Upload First Network")
file1 = st.file_uploader("Upload the first Excel file", type=["xlsx"])

df1 = None
if file1:
    df1 = pd.read_excel(file1, header=1)
    st.write("First network loaded into a DataFrame:")
    st.dataframe(df1)

# Upload second Excel file
st.header("Step 2: Upload Second Network")
file2 = st.file_uploader("Upload the second Excel file", type=["xlsx"])

df2 = None
if file2:
    df2 = pd.read_excel(file2, header=1)
    st.write("Second network loaded into a DataFrame:")
    st.dataframe(df2)

# Merge the dataframes
if df1 is not None and df2 is not None:
    st.header("Step 3: Merge Networks")

    # Get list of all personas from both files
    all_personas = pd.concat([df1["Persona"], df2["Persona"]]).drop_duplicates().tolist()

    # Align both networks to the full list of personas
    def align_network(df, all_personas):
        matrix = df.set_index("Persona")
        matrix = matrix.iloc[:, 4:]  # Only include adjacency data
        matrix = matrix.reindex(index=all_personas, columns=all_personas, fill_value=0)
        return matrix

    aligned_df1 = align_network(df1, all_personas)
    aligned_df2 = align_network(df2, all_personas)

    # Merge the matrices
    def merge_matrices(matrix1, matrix2):
        merged = matrix1.combine(matrix2, lambda x, y: 
            2 if (x == 1 and y == 3) or (x == 3 and y == 1) else 
            2 if x == 2 or y == 2 else 
            max(x, y))
        return merged

    merged_matrix = merge_matrices(aligned_df1, aligned_df2)

    # Reset index and prepare final DataFrame
    merged_df = merged_matrix.reset_index()
    merged_df.insert(0, "Persona", all_personas)  # Ensure Persona column is included

    st.write("Merged DataFrame:")
    st.dataframe(merged_df)

    # Provide download link for the merged DataFrame
    st.header("Step 4: Download Merged DataFrame")

    @st.cache
    def convert_df(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Merged Data')
        return output.getvalue()

    merged_file = convert_df(merged_df)
    st.download_button(
        label="Download Merged DataFrame as Excel",
        data=merged_file,
        file_name="merged_network.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
