import streamlit as st
import pandas as pd

# Streamlit app setup
st.title("Spreadsheet Merger")
st.write("Upload two spreadsheets to merge them into a single file.")

# File upload
uploaded_file1 = st.file_uploader("Upload the first spreadsheet", type="xlsx")
uploaded_file2 = st.file_uploader("Upload the second spreadsheet", type="xlsx")

if uploaded_file1 and uploaded_file2:
    # Load files into dataframes
    df1 = pd.read_excel(uploaded_file1, header=1)
    df2 = pd.read_excel(uploaded_file2, header=1)

    # Ensure consistent columns in both files
    personas_df1 = set(df1.columns[4:])  # Columns after Persona, Handle, Social Handle, Faction
    personas_df2 = set(df2.columns[4:])
    all_personas = sorted(personas_df1.union(personas_df2))

    for persona in all_personas:
        if persona not in df1.columns:
            df1[persona] = ""
        if persona not in df2.columns:
            df2[persona] = ""

    # Merge the spreadsheets
    merged_df = df1.copy()
    for row in df2.itertuples(index=False):
        persona = row[0]  # Persona identifier
        if persona not in merged_df["Persona"].values:
            merged_df = pd.concat([merged_df, pd.DataFrame([row], columns=merged_df.columns)])
        else:
            for idx, col in enumerate(all_personas, start=4):
                val1 = df1.loc[df1["Persona"] == persona, col].values[0]
                val2 = row[idx]

                if pd.isna(val1):
                    merged_value = val2
                elif pd.isna(val2):
                    merged_value = val1
                elif val1 == 2 or val2 == 2:
                    merged_value = 2
                elif (val1 == 1 and val2 == 3) or (val1 == 3 and val2 == 1):
                    merged_value = 2
                else:
                    merged_value = val1

                merged_df.loc[merged_df["Persona"] == persona, col] = merged_value

    # Save the merged dataframe
    output_file = "merged_spreadsheet.xlsx"
    merged_df.to_excel(output_file, index=False)

    st.success("Merge complete!")
    st.download_button(
        label="Download Merged Spreadsheet",
        data=open(output_file, "rb").read(),
        file_name="merged_spreadsheet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )