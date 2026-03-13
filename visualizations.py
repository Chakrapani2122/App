from io import BytesIO

from PIL import Image
import streamlit as st

from github_utils import (
    get_file_bytes,
    get_repo_contents,
    load_visualization_metadata,
    validate_token,
)


def fetch_visualizations(token):
    return get_repo_contents(token, "visualizations") or []


def _sort_visualizations(items, sort_by):
    if sort_by == "Name (A-Z)":
        return sorted(items, key=lambda x: x["name"].lower())
    if sort_by == "Name (Z-A)":
        return sorted(items, key=lambda x: x["name"].lower(), reverse=True)
    if sort_by == "File Size (Small-Large)":
        return sorted(items, key=lambda x: x.get("size", 0))
    if sort_by == "File Size (Large-Small)":
        return sorted(items, key=lambda x: x.get("size", 0), reverse=True)
    return items


def _render_gallery_view(items, token):
    cols_per_row = 2
    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, item in enumerate(row_items):
            with cols[i]:
                image_bytes = get_file_bytes(token, f"visualizations/{item['name']}.png")
                if not image_bytes:
                    st.warning(f"Unable to load {item['name']}")
                    continue
                st.image(Image.open(BytesIO(image_bytes)), caption=item["name"], use_column_width=True)
                st.write(f"**Description:** {item['description']}")
                st.caption(f"Size: {item.get('size', 0)} bytes")
                st.download_button(
                    label="Download plot",
                    data=image_bytes,
                    file_name=f"{item['name']}.png",
                    mime="image/png",
                    key=f"download_gallery_{item['name']}"
                )


def _render_grid_view(items, token):
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, item in enumerate(row_items):
            with cols[i]:
                image_bytes = get_file_bytes(token, f"visualizations/{item['name']}.png")
                if not image_bytes:
                    st.warning(f"Unable to load {item['name']}")
                    continue
                st.image(Image.open(BytesIO(image_bytes)), caption=item["name"], use_column_width=True)
                st.caption(item["description"])
                st.download_button(
                    label="Download",
                    data=image_bytes,
                    file_name=f"{item['name']}.png",
                    mime="image/png",
                    key=f"download_grid_{item['name']}"
                )


def _render_list_view(items, token):
    for item in items:
        image_bytes = get_file_bytes(token, f"visualizations/{item['name']}.png")
        list_cols = st.columns([1, 3, 1])
        with list_cols[0]:
            if image_bytes:
                st.image(Image.open(BytesIO(image_bytes)), use_column_width=True)
            else:
                st.warning("Preview unavailable")
        with list_cols[1]:
            st.write(f"**{item['name']}**")
            st.write(item["description"])
            st.caption(f"Size: {item.get('size', 0)} bytes")
        with list_cols[2]:
            if image_bytes:
                st.download_button(
                    label="Download",
                    data=image_bytes,
                    file_name=f"{item['name']}.png",
                    mime="image/png",
                    key=f"download_list_{item['name']}"
                )
        st.divider()


def show_visualizations_page(github_token: str | None = None, show_header: bool = True):
    if show_header:
        st.title("Visualizations")
        st.write("For better experience, please enable the wide mode.")

    if not github_token:
        github_token = st.session_state.get("github_token")

    if not github_token and show_header:
        input_token = st.text_input("Enter GitHub security token", type="password", key="viz_token_input")
        if input_token:
            if validate_token(input_token):
                st.success("Token validated and saved for this session.")
                st.session_state["github_token"] = input_token
                github_token = input_token
            else:
                st.error("Invalid token or insufficient permissions.")

    if not github_token:
        return

    visualizations = fetch_visualizations(github_token)
    descriptions = load_visualization_metadata(github_token)

    viz_items = []
    for viz in visualizations:
        if viz.get("type") == "file" and viz.get("name", "").lower().endswith(".png"):
            image_name = viz["name"].replace(".png", "")
            metadata_bundle = descriptions.get(image_name, {})
            viz_items.append(
                {
                    "name": image_name,
                    "description": metadata_bundle.get("description", "No description available"),
                    "size": viz.get("size", 0),
                }
            )

    if not viz_items:
        st.info("No visualizations available.")
        return

    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    with control_col1:
        search_query = st.text_input("Search visualizations", placeholder="Search by name or description")
    with control_col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Name (A-Z)", "Name (Z-A)", "File Size (Small-Large)", "File Size (Large-Small)"],
            key="viz_sort_by"
        )
    with control_col3:
        view_mode = st.selectbox("View mode", ["Gallery", "Grid", "List"], key="viz_view_mode")

    filtered_items = viz_items
    if search_query:
        query = search_query.strip().lower()
        filtered_items = [
            item for item in viz_items
            if query in item["name"].lower()
            or query in item["description"].lower()
        ]

    filtered_items = _sort_visualizations(filtered_items, sort_by)

    if not filtered_items:
        st.warning("No visualizations match your search.")
        return

    st.caption(f"Showing {len(filtered_items)} visualization(s)")

    if view_mode == "Gallery":
        _render_gallery_view(filtered_items, github_token)
    elif view_mode == "Grid":
        _render_grid_view(filtered_items, github_token)
    else:
        _render_list_view(filtered_items, github_token)


if __name__ == "__main__":
    show_visualizations_page()
