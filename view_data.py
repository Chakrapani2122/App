from io import BytesIO
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from PIL import Image
from openpyxl.utils.exceptions import InvalidFileException
from pandas.errors import EmptyDataError
from scipy import stats
import streamlit as st

from github_utils import (
    get_file_bytes,
    get_file_metadata,
    get_repo_contents,
    validate_token,
)

SUPPORTED_EXTENSIONS = (
    ".xlsx",
    ".xls",
    ".csv",
    ".txt",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".dat",
    ".docx",
)


def show_column_data_types(df):
    with st.expander("**Show Column Data Types**", expanded=False):
        column_data = []
        for col in df.columns:
            column_data.append({
                "Column Name": col,
                "Data Type": str(df[col].dtype),
            })
        col1, col2 = st.columns(2)
        with col1:
            st.table(pd.DataFrame(column_data[: len(column_data) // 2]).set_index("Column Name"))
        with col2:
            st.table(pd.DataFrame(column_data[len(column_data) // 2 :]).set_index("Column Name"))


def _extract_docx_text(file_content):
    try:
        with zipfile.ZipFile(BytesIO(file_content)) as docx_zip:
            document_xml = docx_zip.read("word/document.xml")
        root = ET.fromstring(document_xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for para in root.findall(".//w:p", ns):
            texts = [node.text for node in para.findall(".//w:t", ns) if node.text]
            if texts:
                paragraphs.append("".join(texts))
        return "\n".join(paragraphs)
    except (KeyError, zipfile.BadZipFile, ET.ParseError):
        return None


def _decode_text_content(file_content):
    try:
        return file_content.decode("utf-8")
    except UnicodeDecodeError:
        return file_content.decode("latin-1", errors="replace")


def _download_raw_file(file_name, file_content, mime="application/octet-stream"):
    st.download_button(
        "Download file",
        data=file_content,
        file_name=file_name,
        mime=mime,
        key=f"download_raw_{file_name}",
    )


def _coerce_scalar(value, series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(value)
    return value


def _apply_pipeline(df, steps):
    transformed = df.copy()

    for step in steps:
        operation = step["operation"]
        if operation == "Filter":
            column = step["column"]
            operator = step["operator"]
            value = _coerce_scalar(step["value"], transformed[column])
            if operator == "==":
                transformed = transformed[transformed[column] == value]
            elif operator == "!=":
                transformed = transformed[transformed[column] != value]
            elif operator == ">":
                transformed = transformed[transformed[column] > value]
            elif operator == ">=":
                transformed = transformed[transformed[column] >= value]
            elif operator == "<":
                transformed = transformed[transformed[column] < value]
            elif operator == "<=":
                transformed = transformed[transformed[column] <= value]
            elif operator == "contains":
                transformed = transformed[
                    transformed[column].astype(str).str.contains(str(value), case=False, na=False)
                ]
        elif operation == "Groupby":
            group_columns = step["group_columns"]
            target_columns = step["target_columns"]
            agg_function = step["agg_function"]
            if target_columns:
                transformed = (
                    transformed.groupby(group_columns, dropna=False)[target_columns]
                    .agg(agg_function)
                    .reset_index()
                )
            else:
                transformed = transformed.groupby(group_columns, dropna=False).size().reset_index(name="count")
        elif operation == "Normalize":
            method = step["method"]
            for column in step["columns"]:
                numeric = pd.to_numeric(transformed[column], errors="coerce")
                if method == "z-score":
                    denom = numeric.std(ddof=0)
                    transformed[f"{column}_zscore"] = 0 if denom == 0 else (numeric - numeric.mean()) / denom
                else:
                    minimum = numeric.min()
                    maximum = numeric.max()
                    denom = maximum - minimum
                    transformed[f"{column}_minmax"] = 0 if denom == 0 else (numeric - minimum) / denom
        elif operation == "Log transform":
            offset = float(step["offset"])
            for column in step["columns"]:
                numeric = pd.to_numeric(transformed[column], errors="coerce")
                shifted = numeric + offset
                if (shifted <= 0).any():
                    raise ValueError(f"Column '{column}' contains values that remain non-positive after offset {offset}.")
                transformed[f"{column}_log"] = np.log(shifted)

    return transformed


def _render_transformation_pipeline(df, file_path):
    state_key = f"pipeline_{file_path}".replace("/", "_")
    steps = st.session_state.setdefault(state_key, [])
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    columns = df.columns.tolist()

    with st.expander("Transformation Pipeline Builder", expanded=False):
        operation = st.selectbox(
            "Operation",
            ["Filter", "Groupby", "Normalize", "Log transform"],
            key=f"pipeline_op_{state_key}",
        )
        input_cols = st.columns(3)

        new_step = None
        if operation == "Filter":
            with input_cols[0]:
                column = st.selectbox("Column", columns, key=f"filter_col_{state_key}")
            with input_cols[1]:
                operator = st.selectbox(
                    "Operator",
                    ["==", "!=", ">", ">=", "<", "<=", "contains"],
                    key=f"filter_op_{state_key}",
                )
            with input_cols[2]:
                value = st.text_input("Value", key=f"filter_value_{state_key}")
            new_step = {"operation": operation, "column": column, "operator": operator, "value": value}
        elif operation == "Groupby":
            with input_cols[0]:
                group_columns = st.multiselect("Group columns", columns, key=f"group_cols_{state_key}")
            with input_cols[1]:
                target_columns = st.multiselect(
                    "Target numeric columns",
                    numeric_columns,
                    key=f"group_targets_{state_key}",
                )
            with input_cols[2]:
                agg_function = st.selectbox(
                    "Aggregation",
                    ["mean", "sum", "median", "max", "min"],
                    key=f"group_agg_{state_key}",
                )
            new_step = {
                "operation": operation,
                "group_columns": group_columns,
                "target_columns": target_columns,
                "agg_function": agg_function,
            }
        elif operation == "Normalize":
            with input_cols[0]:
                selected_columns = st.multiselect("Numeric columns", numeric_columns, key=f"norm_cols_{state_key}")
            with input_cols[1]:
                method = st.selectbox("Method", ["z-score", "min-max"], key=f"norm_method_{state_key}")
            new_step = {"operation": operation, "columns": selected_columns, "method": method}
        else:
            with input_cols[0]:
                selected_columns = st.multiselect("Numeric columns", numeric_columns, key=f"log_cols_{state_key}")
            with input_cols[1]:
                offset = st.number_input("Offset", value=1.0, key=f"log_offset_{state_key}")
            new_step = {"operation": operation, "columns": selected_columns, "offset": offset}

        button_cols = st.columns(3)
        with button_cols[0]:
            if st.button("Add step", key=f"add_pipeline_step_{state_key}"):
                steps.append(new_step)
        with button_cols[1]:
            if st.button("Remove last", key=f"remove_pipeline_step_{state_key}") and steps:
                steps.pop()
        with button_cols[2]:
            if st.button("Reset pipeline", key=f"reset_pipeline_{state_key}"):
                steps.clear()

        if not steps:
            st.info("Add one or more steps to build a reusable transformation pipeline.")
            return df

        st.dataframe(pd.DataFrame(steps).fillna(""), use_container_width=True)

        try:
            transformed_df = _apply_pipeline(df, steps)
            st.write("**Transformed preview (first 100 rows)**")
            st.dataframe(transformed_df.head(100), use_container_width=True)
            return transformed_df
        except Exception as exc:
            st.error(f"Pipeline error: {exc}")
            return df


def _run_t_test(df, value_column, group_column, selected_groups=None):
    working_df = df.dropna(subset=[group_column, value_column]).copy()
    if selected_groups:
        working_df = working_df[working_df[group_column].isin(selected_groups)]
    labels = list(working_df[group_column].dropna().unique())
    groups = [value.dropna() for _, value in working_df.groupby(group_column)[value_column]]
    if len(groups) != 2:
        raise ValueError("t-test requires exactly two groups.")
    shapiro = {
        labels[i]: stats.shapiro(groups[i]).pvalue if len(groups[i]) >= 3 else None
        for i in range(2)
    }
    levene_p = stats.levene(*groups).pvalue
    result = stats.ttest_ind(groups[0], groups[1], equal_var=levene_p > 0.05, nan_policy="omit")
    return {
        "test": "t-test",
        "groups": labels,
        "assumptions": {
            "normality_shapiro_p": shapiro,
            "equal_variance_levene_p": levene_p,
        },
        "statistic": result.statistic,
        "pvalue": result.pvalue,
    }


def _run_mann_whitney(df, value_column, group_column, selected_groups=None):
    working_df = df.dropna(subset=[group_column, value_column]).copy()
    if selected_groups:
        working_df = working_df[working_df[group_column].isin(selected_groups)]
    labels = list(working_df[group_column].dropna().unique())
    groups = [value.dropna() for _, value in working_df.groupby(group_column)[value_column]]
    if len(groups) != 2:
        raise ValueError("Mann-Whitney requires exactly two groups.")
    result = stats.mannwhitneyu(groups[0], groups[1], alternative="two-sided")
    return {
        "test": "Mann-Whitney U",
        "groups": labels,
        "assumptions": {
            "independent_groups": True,
            "ordinal_or_continuous_response": True,
        },
        "statistic": result.statistic,
        "pvalue": result.pvalue,
    }


def _run_anova(df, value_column, group_column, selected_groups=None):
    working_df = df.dropna(subset=[group_column, value_column]).copy()
    if selected_groups:
        working_df = working_df[working_df[group_column].isin(selected_groups)]
    labels = list(working_df[group_column].dropna().unique())
    grouped = [value.dropna() for _, value in working_df.groupby(group_column)[value_column]]
    if len(grouped) < 2:
        raise ValueError("ANOVA requires at least two groups.")
    shapiro = {
        labels[i]: stats.shapiro(grouped[i]).pvalue if len(grouped[i]) >= 3 else None
        for i in range(len(grouped))
    }
    levene_p = stats.levene(*grouped).pvalue
    result = stats.f_oneway(*grouped)
    return {
        "test": "ANOVA",
        "groups": labels,
        "assumptions": {
            "normality_shapiro_p": shapiro,
            "equal_variance_levene_p": levene_p,
        },
        "statistic": result.statistic,
        "pvalue": result.pvalue,
    }


def _run_chi_square(df, first_column, second_column):
    contingency = pd.crosstab(df[first_column], df[second_column])
    statistic, pvalue, _, expected = stats.chi2_contingency(contingency)
    return {
        "test": "Chi-square",
        "assumptions": {
            "min_expected_frequency": float(expected.min()),
            "all_expected_ge_5": bool((expected >= 5).all()),
        },
        "statistic": statistic,
        "pvalue": pvalue,
        "contingency_table": contingency.to_dict(),
    }


def _get_group_candidate_columns(df, numeric_columns, min_groups=2):
    candidate_columns = []
    for column in df.columns:
        if column in numeric_columns and df[column].dtype != "object":
            continue
        group_count = df[column].dropna().nunique()
        if group_count >= min_groups:
            candidate_columns.append(column)
    return candidate_columns


def _get_group_values(df, group_column):
    return [str(value) for value in df[group_column].dropna().astype(str).unique().tolist()]


def _render_statistical_tests(df, file_path):
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = _get_group_candidate_columns(df, numeric_columns, min_groups=2)
    state_prefix = file_path.replace("/", "_")

    with st.expander("Statistical Test Toolkit", expanded=False):
        t_test_tab, anova_tab, mann_whitney_tab, chi_square_tab = st.tabs(
            ["t-test", "ANOVA", "Mann-Whitney", "Chi-square"]
        )

        with t_test_tab:
            if numeric_columns and categorical_columns:
                cols = st.columns(2)
                with cols[0]:
                    value_column = st.selectbox("Value column", numeric_columns, key=f"ttest_value_{file_path}")
                with cols[1]:
                    group_column = st.selectbox("Group column", categorical_columns, key=f"ttest_group_{file_path}")
                group_values = _get_group_values(df, group_column)
                selected_groups = st.multiselect(
                    "Groups to compare",
                    group_values,
                    default=group_values[:2],
                    key=f"ttest_groups_{file_path}",
                )
                if st.button("Run t-test", key=f"run_ttest_{file_path}"):
                    try:
                        if len(selected_groups) != 2:
                            raise ValueError("Select exactly two groups.")
                        st.session_state[f"ttest_result_{state_prefix}"] = _run_t_test(
                            df,
                            value_column,
                            group_column,
                            selected_groups=selected_groups,
                        )
                    except Exception as exc:
                        st.error(str(exc))
                ttest_result = st.session_state.get(f"ttest_result_{state_prefix}")
                if ttest_result:
                    st.json(ttest_result)
            else:
                st.info("Need at least one numeric column and one grouping column.")

        with anova_tab:
            if numeric_columns and categorical_columns:
                cols = st.columns(2)
                with cols[0]:
                    value_column = st.selectbox("Value column", numeric_columns, key=f"anova_value_{file_path}")
                with cols[1]:
                    group_column = st.selectbox("Group column", categorical_columns, key=f"anova_group_{file_path}")
                available_groups = _get_group_values(df, group_column)
                selected_groups = st.multiselect(
                    "Groups to compare",
                    available_groups,
                    default=available_groups[: min(3, len(available_groups))],
                    key=f"anova_groups_{file_path}",
                )
                if st.button("Run ANOVA", key=f"run_anova_{file_path}"):
                    try:
                        st.session_state[f"anova_result_{state_prefix}"] = _run_anova(
                            df,
                            value_column,
                            group_column,
                            selected_groups=selected_groups,
                        )
                    except Exception as exc:
                        st.error(str(exc))
                anova_result = st.session_state.get(f"anova_result_{state_prefix}")
                if anova_result:
                    st.json(anova_result)
            else:
                st.info("Need at least one numeric column and one grouping column.")

        with mann_whitney_tab:
            if numeric_columns and categorical_columns:
                cols = st.columns(2)
                with cols[0]:
                    value_column = st.selectbox("Value column", numeric_columns, key=f"mw_value_{file_path}")
                with cols[1]:
                    group_column = st.selectbox("Group column", categorical_columns, key=f"mw_group_{file_path}")
                group_values = _get_group_values(df, group_column)
                selected_groups = st.multiselect(
                    "Groups to compare",
                    group_values,
                    default=group_values[:2],
                    key=f"mw_groups_{file_path}",
                )
                if st.button("Run Mann-Whitney", key=f"run_mw_{file_path}"):
                    try:
                        if len(selected_groups) != 2:
                            raise ValueError("Select exactly two groups.")
                        st.session_state[f"mw_result_{state_prefix}"] = _run_mann_whitney(
                            df,
                            value_column,
                            group_column,
                            selected_groups=selected_groups,
                        )
                    except Exception as exc:
                        st.error(str(exc))
                mw_result = st.session_state.get(f"mw_result_{state_prefix}")
                if mw_result:
                    st.json(mw_result)
            else:
                st.info("Need at least one numeric column and one grouping column.")

        with chi_square_tab:
            if len(categorical_columns) >= 2:
                cols = st.columns(2)
                with cols[0]:
                    first_column = st.selectbox("First categorical column", categorical_columns, key=f"chi_a_{file_path}")
                with cols[1]:
                    second_column = st.selectbox("Second categorical column", categorical_columns, key=f"chi_b_{file_path}")
                if st.button("Run Chi-square", key=f"run_chi_{file_path}"):
                    try:
                        st.session_state[f"chi_result_{state_prefix}"] = _run_chi_square(df, first_column, second_column)
                    except Exception as exc:
                        st.error(str(exc))
                chi_result = st.session_state.get(f"chi_result_{state_prefix}")
                if chi_result:
                    st.json(chi_result)
            else:
                st.info("Need at least two categorical columns.")


def _show_data_insights(df):
    with st.expander("**Expand to view data insights**", expanded=False):
        if df is not None:
            st.write(f"**Shape:** {df.shape[0]} rows and {df.shape[1]} columns")
            missing_values = pd.DataFrame(
                {
                    "Column Name": df.columns,
                    "Missing Values": df.isnull().sum().values,
                }
            )
            missing_values = missing_values[missing_values["Missing Values"] > 0]
            if not missing_values.empty:
                st.write("**Missing Values:**")
                cols = st.columns(4)
                for i, row in missing_values.iterrows():
                    with cols[i % 4]:
                        st.write(f"{row['Column Name']}: {row['Missing Values']}")
            else:
                st.write("**Missing Values:** There are no missing values in this sheet.")
            st.write("**Descriptive Analysis:**")
            st.dataframe(df.describe(include="all").transpose().fillna(""), use_container_width=True)
        else:
            st.warning("No data available to display insights.")


def display_file_content(token, path):
    metadata = get_file_metadata(token, path)
    if not metadata or metadata.get("type") != "file":
        st.error("Selected path is not a file.")
        return None

    file_content = get_file_bytes(token, path)
    if file_content is None:
        st.error("Failed to retrieve file content.")
        return None

    file_name = path.split("/")[-1]
    lower_path = path.lower()

    if lower_path.endswith((".xlsx", ".xls")):
        try:
            workbook = pd.ExcelFile(BytesIO(file_content), engine="openpyxl")
            sheet = st.selectbox("Select sheet", workbook.sheet_names, key=f"sheet_select_{path}")
            full_df = pd.read_excel(BytesIO(file_content), sheet_name=sheet)
            st.dataframe(full_df, use_container_width=True)
            show_column_data_types(full_df)
            return full_df
        except InvalidFileException:
            st.error("The Excel file appears to be invalid or corrupted.")
            _download_raw_file(file_name, file_content)
            return None
        except Exception as exc:
            st.error(f"An error occurred while reading the Excel file: {exc}")
            _download_raw_file(file_name, file_content)
            return None

    if lower_path.endswith(".csv"):
        try:
            full_df = pd.read_csv(BytesIO(file_content))
            st.dataframe(full_df, use_container_width=True)
            show_column_data_types(full_df)
            return full_df
        except EmptyDataError:
            st.error("The CSV file is empty or improperly formatted.")
            _download_raw_file(file_name, file_content, mime="text/csv")
            return None
        except Exception as exc:
            st.error(f"An error occurred while reading the CSV file: {exc}")
            _download_raw_file(file_name, file_content, mime="text/csv")
            return None

    if lower_path.endswith((".txt", ".md", ".dat")):
        st.text_area(
            "Read-only preview",
            _decode_text_content(file_content),
            height=400,
            disabled=True,
            key=f"readonly_text_{path}".replace("/", "_"),
        )
        _download_raw_file(file_name, file_content, mime="text/plain")
        return None

    if lower_path.endswith(".docx"):
        docx_text = _extract_docx_text(file_content)
        if docx_text is None:
            st.error("Unable to parse this .docx file.")
            _download_raw_file(file_name, file_content)
            return None
        st.text_area(
            "Read-only DOCX preview",
            docx_text,
            height=400,
            disabled=True,
            key=f"readonly_docx_{path}".replace("/", "_"),
        )
        _download_raw_file(file_name, file_content)
        return None

    if lower_path.endswith((".jpg", ".jpeg", ".png")):
        st.image(Image.open(BytesIO(file_content)), caption=file_name)
        _download_raw_file(file_name, file_content, mime="image/png")
        return None

    st.warning("Preview is not available for this file type. You can still download it below.")
    _download_raw_file(file_name, file_content)
    return None


def show_view_data_page():
    st.title("View Data")

    token = st.session_state.get("github_token")
    if not token:
        input_token = st.text_input("Enter security token", type="password", key="github_token_view")
        if input_token:
            if validate_token(input_token):
                st.success("Token validated successfully and saved for this session.")
                st.session_state["github_token"] = input_token
                token = input_token
            else:
                st.error("Invalid token.")

    if not token:
        return

    st.write("**Select File**")
    dropdown_specs = []
    selected_file_path = None
    path_so_far = ""

    while True:
        contents = get_repo_contents(token, path_so_far)
        if contents is None:
            st.error("Failed to load folder contents. Please verify your token or try again.")
            break

        dirs = sorted(
            [
                item
                for item in contents
                if item["type"] == "dir" and not (path_so_far == "" and item["name"].lower() == "visualizations")
            ],
            key=lambda x: x["name"].lower(),
        )
        files = sorted(
            [
                item
                for item in contents
                if item["type"] == "file" and item["name"].lower().endswith(SUPPORTED_EXTENSIONS)
            ],
            key=lambda x: x["name"].lower(),
        )

        dir_names = [d["name"] for d in dirs]
        file_names = [f["name"] for f in files]

        if not dir_names and not file_names:
            break

        options = ["-- Select --"] + dir_names + file_names
        nav_key = f"nav_{path_so_far or 'root'}"
        folder_label = path_so_far.split("/")[-1] if path_so_far else "Root"

        dropdown_specs.append(
            {
                "key": nav_key,
                "label": f"📂 {folder_label}",
                "options": options,
                "dir_names": dir_names,
                "file_names": file_names,
            }
        )

        current_val = st.session_state.get(nav_key, "-- Select --")
        if current_val not in (dir_names + file_names):
            break

        if current_val in file_names:
            selected_file_path = f"{path_so_far}/{current_val}" if path_so_far else current_val
            break

        path_so_far = f"{path_so_far}/{current_val}" if path_so_far else current_val

    for row_start in range(0, len(dropdown_specs), 3):
        row_specs = dropdown_specs[row_start : row_start + 3]
        cols = st.columns(3)
        for i, spec in enumerate(row_specs):
            with cols[i]:
                dir_names = spec["dir_names"]

                def fmt(name, folder_names=dir_names):
                    if name == "-- Select --":
                        return "-- Select --"
                    return f"📁 {name}" if name in folder_names else f"📄 {name}"

                st.selectbox(spec["label"], spec["options"], format_func=fmt, key=spec["key"])

    if selected_file_path:
        st.write("**File Contents**")
        df = display_file_content(token, selected_file_path)
        if df is not None:
            _show_data_insights(df)
            transformed_df = _render_transformation_pipeline(df, selected_file_path)
            _render_statistical_tests(transformed_df, selected_file_path)
