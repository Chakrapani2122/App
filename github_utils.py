import base64
from io import BytesIO
import xml.etree.ElementTree as ET

import requests
import streamlit as st

GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
REQUEST_TIMEOUT = 30
VISUALIZATION_METADATA_PATH = "visualizations/descriptions.xml"


def github_headers(token, accept="application/vnd.github.v3+json"):
    return {
        "Authorization": f"token {token}",
        "Accept": accept,
    }


def _request(method, url, token, **kwargs):
    headers = github_headers(token)
    extra_headers = kwargs.pop("headers", None)
    if extra_headers:
        headers.update(extra_headers)
    return requests.request(method, url, headers=headers, timeout=REQUEST_TIMEOUT, **kwargs)


@st.cache_data(ttl=300)
def validate_token(token):
    response = _request("GET", f"https://api.github.com/repos/{GITHUB_REPO}", token)
    return response.status_code == 200


@st.cache_data(ttl=300)
def get_repo_contents(token, path=""):
    response = _request("GET", f"{GITHUB_API_URL}{path}", token)
    if response.status_code == 200:
        payload = response.json()
        return payload if isinstance(payload, list) else None
    return None


@st.cache_data(ttl=300)
def get_file_metadata(token, path):
    response = _request("GET", f"{GITHUB_API_URL}{path}", token)
    if response.status_code == 200:
        payload = response.json()
        return payload if isinstance(payload, dict) else None
    return None


@st.cache_data(ttl=300)
def get_file_bytes(token, path):
    metadata = get_file_metadata(token, path)
    if not metadata or metadata.get("type") != "file":
        return None

    download_url = metadata.get("download_url")
    if download_url:
        response = requests.get(
            download_url,
            headers=github_headers(token, accept="application/vnd.github.v3.raw"),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.content

    if metadata.get("content"):
        return base64.b64decode(metadata["content"])

    return None


@st.cache_data(ttl=300)
def fetch_visualization_descriptions(token):
    metadata = get_file_metadata(token, VISUALIZATION_METADATA_PATH)
    if metadata and metadata.get("content"):
        return base64.b64decode(metadata["content"]).decode("utf-8")
    return None


def load_visualization_metadata(token):
    description_xml = fetch_visualization_descriptions(token)
    descriptions = {}
    if not description_xml:
        return descriptions

    try:
        root = ET.fromstring(description_xml)
    except ET.ParseError:
        return descriptions
    for viz in root.findall("Visualization"):
        name_node = viz.find("Name")
        if name_node is None or not name_node.text:
            continue

        description_node = viz.find("Description")
        metadata_node = viz.find("Metadata")
        descriptions[name_node.text] = {
            "description": description_node.text if description_node is not None and description_node.text else "No description available",
            "metadata": {
                child.tag: child.text or ""
                for child in (list(metadata_node) if metadata_node is not None else [])
            },
        }
    return descriptions


def get_file_sha(path, token):
    metadata = get_file_metadata(token, path)
    if metadata:
        return metadata.get("sha")
    return None


def upload_bytes_to_github(file_bytes, path, token, message, sha=None):
    url = f"{GITHUB_API_URL}{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(file_bytes).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(
        url,
        json=payload,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
        timeout=REQUEST_TIMEOUT,
    )
    return response.status_code, response.json()


def save_visualization_metadata(token, name, description, metadata_dict=None):
    xml_sha = get_file_sha(VISUALIZATION_METADATA_PATH, token)
    xml_content = fetch_visualization_descriptions(token)

    if xml_content:
        root = ET.fromstring(xml_content)
    else:
        root = ET.Element("Visualizations")

    existing = None
    for viz in root.findall("Visualization"):
        node = viz.find("Name")
        if node is not None and node.text == name:
            existing = viz
            break

    if existing is not None:
        root.remove(existing)

    visualization = ET.Element("Visualization")
    ET.SubElement(visualization, "Name").text = name
    ET.SubElement(visualization, "Description").text = description
    if metadata_dict:
        metadata_node = ET.SubElement(visualization, "Metadata")
        for key, value in metadata_dict.items():
            ET.SubElement(metadata_node, key).text = str(value)
    root.append(visualization)

    xml_buffer = BytesIO()
    ET.ElementTree(root).write(xml_buffer, encoding="utf-8", xml_declaration=True)
    xml_buffer.seek(0)
    return upload_bytes_to_github(
        xml_buffer.read(),
        VISUALIZATION_METADATA_PATH,
        token,
        f"Update visualization metadata: {name}",
        sha=xml_sha,
    )


def clear_github_caches():
    validate_token.clear()
    get_repo_contents.clear()
    get_file_metadata.clear()
    get_file_bytes.clear()
    fetch_visualization_descriptions.clear()
