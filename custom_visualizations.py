from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from github_utils import (
    clear_github_caches,
    get_file_bytes,
    get_repo_contents,
    save_visualization_metadata,
    upload_bytes_to_github,
    validate_token,
)

PLOT_TYPES = [
    "Scatter Plot",
    "Line Plot",
    "Bar Plot",
    "Histogram",
    "Box Plot",
    "Violin Plot",
    "Heatmap",
    "Regression Plot",
    "Density Plot",
    "Swarm Plot",
    "Pair Plot",
]


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


def _repo_file_nav_grid(token, nav_prefix):
    dropdown_specs = []
    current_path = ""
    selected_file_path = None

    while True:
        contents = get_repo_contents(token, current_path)
        if not contents:
            break

        dirs = sorted(
            [
                item
                for item in contents
                if item["type"] == "dir" and not (current_path == "" and item["name"].lower() == "visualizations")
            ],
            key=lambda x: x["name"].lower(),
        )
        files = sorted(
            [item for item in contents if item["type"] == "file" and item["name"].lower().endswith((".xlsx", ".csv"))],
            key=lambda x: x["name"].lower(),
        )
        dir_names = [d["name"] for d in dirs]
        file_names = [f["name"] for f in files]

        if not dir_names and not file_names:
            break

        nav_key = f"{nav_prefix}_{current_path or 'root'}"
        dropdown_specs.append(
            {
                "key": nav_key,
                "label": f"📂 {current_path.split('/')[-1] if current_path else 'Root'}",
                "options": ["-- Select --"] + dir_names + file_names,
                "dir_names": dir_names,
                "file_names": file_names,
            }
        )

        selected_value = st.session_state.get(nav_key, "-- Select --")
        if selected_value not in dir_names + file_names:
            break
        if selected_value in file_names:
            selected_file_path = f"{current_path}/{selected_value}" if current_path else selected_value
            break
        current_path = f"{current_path}/{selected_value}" if current_path else selected_value

    for row_start in range(0, len(dropdown_specs), 3):
        row_specs = dropdown_specs[row_start : row_start + 3]
        cols = st.columns(3)
        for index, spec in enumerate(row_specs):
            with cols[index]:
                folder_names = spec["dir_names"]

                def fmt(name, directory_names=folder_names):
                    if name == "-- Select --":
                        return name
                    return f"📁 {name}" if name in directory_names else f"📄 {name}"

                st.selectbox(spec["label"], spec["options"], format_func=fmt, key=spec["key"])

    return selected_file_path


def _load_dataset_from_bytes(file_bytes, file_name, key_prefix):
    lower_name = file_name.lower()
    if lower_name.endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))

    workbook = pd.ExcelFile(BytesIO(file_bytes))
    sheet = st.selectbox("Select a sheet", workbook.sheet_names, key=f"sheet_{key_prefix}")
    return pd.read_excel(BytesIO(file_bytes), sheet_name=sheet)


def _render_plot_config(df, key_prefix, comparative_mode=False):
    available_plot_types = [plot for plot in PLOT_TYPES if not (comparative_mode and plot == "Pair Plot")]
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    columns = df.columns.tolist()

    selector_cols = st.columns(3)
    with selector_cols[0]:
        plot_type = st.selectbox("Plot Type", available_plot_types, key=f"plot_type_{key_prefix}")
    config = {"plot_type": plot_type}

    if plot_type in {"Scatter Plot", "Line Plot", "Bar Plot", "Regression Plot"}:
        with selector_cols[1]:
            config["x_column"] = st.selectbox("X-axis", columns, key=f"x_{key_prefix}")
        with selector_cols[2]:
            config["y_columns"] = st.multiselect("Y-axis columns", numeric_columns, key=f"y_{key_prefix}")
    elif plot_type in {"Box Plot", "Violin Plot", "Swarm Plot"}:
        with selector_cols[1]:
            config["x_column"] = st.selectbox("X-axis", columns, key=f"x_{key_prefix}")
        with selector_cols[2]:
            config["y_column"] = st.selectbox("Y-axis", numeric_columns, key=f"y_single_{key_prefix}")
    elif plot_type in {"Histogram", "Density Plot"}:
        with selector_cols[1]:
            config["x_column"] = st.selectbox("X-axis", numeric_columns, key=f"hist_x_{key_prefix}")
    elif plot_type == "Heatmap":
        with selector_cols[1]:
            config["selected_columns"] = st.multiselect(
                "Y-axis columns",
                numeric_columns,
                default=numeric_columns[: min(5, len(numeric_columns))],
                key=f"heat_cols_{key_prefix}",
            )
    elif plot_type == "Pair Plot":
        with selector_cols[1]:
            config["selected_columns"] = st.multiselect(
                "Y-axis columns",
                numeric_columns,
                default=numeric_columns[: min(4, len(numeric_columns))],
                key=f"pair_cols_{key_prefix}",
            )

    label_cols = st.columns(3)
    with label_cols[0]:
        config["plot_title"] = st.text_input("Plot Title", key=f"plot_title_{key_prefix}")
    with label_cols[1]:
        config["x_label"] = st.text_input("X-axis Label", key=f"x_label_{key_prefix}")
    with label_cols[2]:
        config["y_label"] = st.text_input("Y-axis Label", key=f"y_label_{key_prefix}")
    return config


def _plot_on_axis(ax, df, config, title):
    plot_type = config["plot_type"]
    if plot_type == "Scatter Plot":
        for column in config["y_columns"]:
            sns.scatterplot(data=df, x=config["x_column"], y=column, ax=ax, label=column)
    elif plot_type == "Line Plot":
        for column in config["y_columns"]:
            sns.lineplot(data=df, x=config["x_column"], y=column, ax=ax, label=column)
    elif plot_type == "Bar Plot":
        for column in config["y_columns"]:
            sns.barplot(data=df, x=config["x_column"], y=column, ax=ax, label=column)
    elif plot_type == "Histogram":
        sns.histplot(data=df, x=config["x_column"], bins=30, ax=ax)
    elif plot_type == "Box Plot":
        sns.boxplot(data=df, x=config["x_column"], y=config["y_column"], ax=ax)
    elif plot_type == "Violin Plot":
        sns.violinplot(data=df, x=config["x_column"], y=config["y_column"], ax=ax)
    elif plot_type == "Heatmap":
        columns = config["selected_columns"] or df.select_dtypes(include="number").columns.tolist()
        sns.heatmap(df[columns].corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
    elif plot_type == "Regression Plot":
        for column in config["y_columns"]:
            sns.regplot(data=df, x=config["x_column"], y=column, ax=ax, label=column)
    elif plot_type == "Density Plot":
        sns.kdeplot(data=df, x=config["x_column"], fill=True, ax=ax)
    elif plot_type == "Swarm Plot":
        sns.swarmplot(data=df, x=config["x_column"], y=config["y_column"], ax=ax)
    else:
        raise ValueError("Unsupported comparative plot type.")

    ax.set_title(config.get("plot_title") or title)
    if config.get("x_label"):
        ax.set_xlabel(config["x_label"])
    if config.get("y_label"):
        ax.set_ylabel(config["y_label"])
    _, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend()


def _generate_plot_figure(df, primary_config, comparative_mode=False, secondary_config=None, share_x=False, share_y=False):
    if primary_config["plot_type"] == "Pair Plot" and not comparative_mode:
        selected_columns = primary_config["selected_columns"]
        if not selected_columns:
            raise ValueError("Select at least one column for the pair plot.")
        grid = sns.pairplot(df[selected_columns].dropna())
        figure = grid.figure
        if primary_config.get("plot_title"):
            figure.suptitle(primary_config["plot_title"], y=1.02)
        if primary_config.get("x_label") and hasattr(figure, "supxlabel"):
            figure.supxlabel(primary_config["x_label"])
        if primary_config.get("y_label") and hasattr(figure, "supylabel"):
            figure.supylabel(primary_config["y_label"])
        return figure

    if comparative_mode:
        figure, axes = plt.subplots(1, 2, figsize=(16, 6), sharex=share_x, sharey=share_y)
        _plot_on_axis(axes[0], df, primary_config, "Primary Plot")
        _plot_on_axis(axes[1], df, secondary_config, "Comparison Plot")
        figure.tight_layout()
        return figure

    figure, axis = plt.subplots(figsize=(10, 6))
    _plot_on_axis(axis, df, primary_config, primary_config["plot_type"])
    figure.tight_layout()
    return figure


def show_custom_visualizations_page(github_token: str | None = None, show_header: bool = True):
    if show_header:
        st.title("🎨 Custom Visualizations")
        st.markdown("**Visualize your data, compare plots, and save them.**")

    if not github_token:
        github_token = st.session_state.get("github_token")
    if not github_token and show_header:
        input_token = st.text_input("**Enter security token**", type="password", key="custom_viz_token_input")
        if input_token:
            if validate_token(input_token):
                st.success("Token validated and saved for this session.")
                st.session_state["github_token"] = input_token
                github_token = input_token
            else:
                st.error("Invalid token or insufficient permissions.")

    df = None
    dataset_name = None
    source_identifier = None
    if github_token:
        st.write("**Select a file from the repository or upload a new file**")
        option = st.radio("Choose an option", ["Select from repository", "Upload new file"], key="file_option")

        if option == "Select from repository":
            selected_file_path = _repo_file_nav_grid(github_token, "cv_nav")
            if selected_file_path:
                file_bytes = get_file_bytes(github_token, selected_file_path)
                if file_bytes is None:
                    st.error("Unable to load the selected file.")
                else:
                    dataset_name = selected_file_path.split("/")[-1]
                    source_identifier = selected_file_path
                    df = _load_dataset_from_bytes(file_bytes, dataset_name, selected_file_path.replace("/", "_"))
            else:
                st.info("Please select a file to start building visualizations.")
        else:
            uploaded_file = st.file_uploader("**Choose a CSV or Excel file**", type=["csv", "xlsx"])
            if uploaded_file is not None:
                dataset_name = uploaded_file.name
                source_identifier = uploaded_file.name
                df = _load_dataset_from_bytes(uploaded_file.getvalue(), uploaded_file.name, uploaded_file.name.replace(".", "_"))

        if df is None:
            st.info("Please select a file to start building visualizations.")
            return

        with st.expander("**Data Snapshot**", expanded=False):
            st.dataframe(df, use_container_width=True)
        show_column_data_types(df)
        st.write("---")

        st.write("**Visualization Builder**")
        comparative_mode = st.checkbox("Enable comparative visualization mode", key="comparative_mode")
        if comparative_mode:
            compare_cols = st.columns(2)
            with compare_cols[0]:
                st.markdown("**Primary plot**")
                primary_config = _render_plot_config(df, "primary", comparative_mode=True)
            with compare_cols[1]:
                st.markdown("**Comparison plot**")
                secondary_config = _render_plot_config(df, "secondary", comparative_mode=True)
            link_cols = st.columns(2)
            with link_cols[0]:
                share_x = st.checkbox("Link X-axes", key="share_x")
            with link_cols[1]:
                share_y = st.checkbox("Link Y-axes", key="share_y")
        else:
            primary_config = _render_plot_config(df, "primary", comparative_mode=False)
            secondary_config = None
            share_x = False
            share_y = False

        if st.button("Generate Plot"):
            try:
                figure = _generate_plot_figure(
                    df,
                    primary_config,
                    comparative_mode=comparative_mode,
                    secondary_config=secondary_config,
                    share_x=share_x,
                    share_y=share_y,
                )
                img_buffer = BytesIO()
                figure.savefig(img_buffer, format="png", bbox_inches="tight")
                img_buffer.seek(0)
                st.session_state["plot_image"] = img_buffer.getvalue()
                plt.close(figure)
            except Exception as exc:
                st.error(f"Error generating plot: {exc}")

        if "plot_image" in st.session_state:
            st.image(st.session_state["plot_image"], caption="Generated Plot", use_column_width=True)
            st.download_button(
                "Download Generated Plot (PNG)",
                data=st.session_state["plot_image"],
                file_name="generated_visualization.png",
                mime="image/png",
                key="download_generated_plot_png",
            )
            plot_name = st.text_input("**Enter the name for the visualization**")
            plot_description = st.text_area("**Enter the description for the visualization**")
            created_by = st.text_input("**Created by**", key="plot_created_by")

            if st.button("Upload Visualization"):
                if not plot_name.strip():
                    st.error("Please enter a visualization name before uploading.")
                elif not plot_description.strip():
                    st.error("Please enter a visualization description before uploading.")
                else:
                    img_status, _ = upload_bytes_to_github(
                        st.session_state["plot_image"],
                        f"visualizations/{plot_name}.png",
                        github_token,
                        f"Upload visualization image: {plot_name}",
                    )
                    xml_status, _ = save_visualization_metadata(github_token, plot_name, plot_description)
                    if img_status == 201 and xml_status in [200, 201]:
                        clear_github_caches()
                        st.success("Visualization uploaded successfully.")
                    else:
                        st.error("Failed to upload visualization.")


if __name__ == "__main__":
    show_custom_visualizations_page()
