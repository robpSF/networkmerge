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
    df1 = pd.read_excel(uploaded_file1, header=None)
    df2 = pd.read_excel(uploaded_file2, header=None)

    # Extract personas and factions from Row 1 and Row 2
    personas_df1 = df1.iloc[0, 4:].tolist()  # Row 1, Columns E onward
    factions_df1 = df1.iloc[1, 4:].tolist()  # Row 2, Columns E onward

    st.write(personas_df1)
    st.write(factions_df1)

    personas_df2 = df2.iloc[0, 4:].tolist()  # Row 1, Columns E onward
    factions_df2 = df2.iloc[1, 4:].tolist()  # Row 2, Columns E onward

    st.write(personas_df2)
    st.write(factions_df2)

    # Extract data rows starting from Row 3
    data_df1 = df1.iloc[2:].reset_index(drop=True)  # Data from Row 3 onward
    data_df2 = df2.iloc[2:].reset_index(drop=True)

    # Add missing personas to each dataset
    all_personas = sorted(set(personas_df1 + personas_df2))

    for persona in all_personas:
        if persona not in personas_df1:
            data_df1[persona] = ""
        if persona not in personas_df2:
            data_df2[persona] = ""

    # Merge the datasets
    merged_df = data_df1.copy()
    for _, row in data_df2.iterrows():
        persona = row[0]  # Assume Persona column is the first column
        if persona not in merged_df.iloc[:, 0].values:
            merged_df = pd.concat([merged_df, pd.DataFrame([row], columns=merged_df.columns)])
        else:
            for col in all_personas:
                val1 = data_df1.loc[data_df1.iloc[:, 0] == persona, col].values[0]
                val2 = row[col]

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

                merged_df.loc[merged_df.iloc[:, 0] == persona, col] = merged_value

    # Add headers back
    merged_df.columns = df1.iloc[1]  # Use headers from Row 2
    merged_df.loc[-1] = [None, None, None, None] + all_personas  # Add Row 1 personas
    merged_df.index = merged_df.index + 1  # Shift index
    merged_df.sort_index(inplace=True)

    # Save the merged dataframe
    output_file = "merged_spreadsheet.xlsx"
    merged_df.to_excel(output_file, index=False, header=False)

    st.success("Merge complete!")
    st.download_button(
        label="Download Merged Spreadsheet",
        data=open(output_file, "rb").read(),
        file_name="merged_spreadsheet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
