import streamlit as st
import requests
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
import base64

# GitHub repository details
GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/visualizations/"

@st.cache_data(ttl=300)
def fetch_visualizations(token):
    # Return list of files in the visualizations folder. Cached for 5 minutes.
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        # Let caller handle errors; return empty list to avoid crashes
        return []

@st.cache_data(ttl=300)
def fetch_description(token):
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(GITHUB_API_URL + "descriptions.xml", headers=headers)
    if response.status_code == 200:
        return base64.b64decode(response.json()['content']).decode('utf-8')
    else:
        return None


@st.cache_data(ttl=300)
def fetch_image_bytes(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    return None


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


def _render_gallery_view(items):
    cols_per_row = 2
    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, item in enumerate(row_items):
            with cols[i]:
                image_bytes = fetch_image_bytes(item["download_url"])
                if not image_bytes:
                    st.warning(f"Unable to load {item['name']}")
                    continue

                image = Image.open(BytesIO(image_bytes))
                st.image(image, caption=item["name"], use_container_width=True)
                st.write(f"**Description:** {item['description']}")
                st.caption(f"Size: {item.get('size', 0)} bytes")
                st.download_button(
                    label="Download plot",
                    data=image_bytes,
                    file_name=f"{item['name']}.png",
                    mime="image/png",
                    key=f"download_gallery_{item['name']}"
                )


def _render_grid_view(items):
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        row_items = items[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for i, item in enumerate(row_items):
            with cols[i]:
                image_bytes = fetch_image_bytes(item["download_url"])
                if image_bytes:
                    image = Image.open(BytesIO(image_bytes))
                    st.image(image, caption=item["name"], use_container_width=True)
                    st.caption(item["description"])
                    st.download_button(
                        label="Download",
                        data=image_bytes,
                        file_name=f"{item['name']}.png",
                        mime="image/png",
                        key=f"download_grid_{item['name']}"
                    )
                else:
                    st.warning(f"Unable to load {item['name']}")


def _render_list_view(items):
    for item in items:
        image_bytes = fetch_image_bytes(item["download_url"])
        list_cols = st.columns([1, 3, 1])
        with list_cols[0]:
            if image_bytes:
                image = Image.open(BytesIO(image_bytes))
                st.image(image, use_container_width=True)
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
    # Optionally render header/subtitle when used as a standalone page
    if show_header:
        st.title("📈 Visualizations")
        st.write("For better experience, please enable the wide mode.")

    # If token wasn't provided, try to read from session state
    if not github_token:
        github_token = st.session_state.get('github_token')

    # If still no token and header is shown, prompt for it here and validate/persist
    if not github_token and show_header:
        input_token = st.text_input("Enter GitHub security token", type="password", key="viz_token_input")
        if input_token:
            # quick validation call
            headers = {"Authorization": f"token {input_token}"}
            test = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}", headers=headers)
            if test.status_code == 200:
                st.success("Token validated and saved for this session.")
                st.session_state['github_token'] = input_token
                github_token = input_token
            else:
                st.error("Invalid token or insufficient permissions.")

    if github_token:
        visualizations = fetch_visualizations(github_token)
        description_xml = fetch_description(github_token)

        descriptions = {}
        if description_xml:
            try:
                root = ET.fromstring(description_xml)
                for viz in root.findall("Visualization"):
                    name = viz.find("Name").text
                    description = viz.find("Description").text
                    descriptions[name] = description
            except ET.ParseError as e:
                st.error(f"Failed to parse descriptions XML: {e}")

        viz_items = []
        for viz in visualizations:
            if viz.get('type') == 'file' and viz.get('name', '').lower().endswith('.png'):
                image_name = viz['name'].replace('.png', '')
                viz_items.append({
                    "name": image_name,
                    "description": descriptions.get(image_name, "No description available"),
                    "download_url": viz.get('download_url'),
                    "size": viz.get('size', 0)
                })

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
                if query in item["name"].lower() or query in item["description"].lower()
            ]

        filtered_items = _sort_visualizations(filtered_items, sort_by)

        if not filtered_items:
            st.warning("No visualizations match your search.")
            return

        st.caption(f"Showing {len(filtered_items)} visualization(s)")

        if view_mode == "Gallery":
            _render_gallery_view(filtered_items)
        elif view_mode == "Grid":
            _render_grid_view(filtered_items)
        else:
            _render_list_view(filtered_items)

if __name__ == "__main__":
    show_visualizations_page()
