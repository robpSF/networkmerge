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

    # Merge logic
    merged_df = pd.merge(
        df1, df2, how="outer", on=["Persona", "Handle", "Social Handle", "Faction"], suffixes=("_1", "_2")
    )

    for col in df1.columns[4:]:  # Assuming columns 4 onward are the connections
        if col in df2.columns:
            merged_col = merged_df[[f"{col}_1", f"{col}_2"]].fillna(0).astype(int)
            
            def resolve_connection(row):
                val1, val2 = row
                if val1 == 1 and val2 == 3 or val1 == 3 and val2 == 1:
                    return 2  # They follow each other
                if val1 == 2 or val2 == 2:
                    return 2  # Mutual connection
                return max(val1, val2)  # Otherwise, take the stronger connection

            merged_df[col] = merged_col.apply(resolve_connection, axis=1)

    merged_df.drop(columns=[col for col in merged_df.columns if col.endswith("_1") or col.endswith("_2")], inplace=True)

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
