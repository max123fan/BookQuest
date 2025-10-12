import requests
from bs4 import BeautifulSoup, SoupStrainer

def get_kcls_availability(title, url, timeout=15):
    """
    Check if a given book title is available at KCLS using its catalog URL.
    Starts parsing after the first 'manifestation-item cp-manifestation-list-item row' div.
    Returns True or False based on availability and prints status messages.
    """
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return False

    html = resp.content  # bytes
    # Convert to string to locate div easily
    html_str = html.decode('utf-8', errors='ignore')

    # Find index of the first manifestation-item div
    start_marker = '<div class="manifestation-item cp-manifestation-list-item row"'
    start_index = html_str.find(start_marker)
    if start_index == -1:
        print("Start marker div not found.")
        return False

    # Slice the HTML from that point onward
    html_sub = html_str[start_index:]

    # Wrap fragment in root for safe parsing
    fragment = f"<html><body>{html_sub}</body></html>"

    title_lower = title.lower().strip()
    only_blocks = SoupStrainer('div', class_='manifestation-item-availability-block-wrap')

    soup = BeautifulSoup(fragment, 'lxml', parse_only=only_blocks)

    for block in soup:
        sr_span = block.find('span', class_='cp-screen-reader-message')
        if sr_span and title_lower in sr_span.get_text(strip=True).lower():
            status = block.find('span', class_='cp-availability-status')
            if status:
                status_str = status.get_text(strip=True).lower()
                if status_str == "all copies in use" or status_str == "unavailable":
                    print(status_str)
                    return False
                print(status_str)
                return True
            else:
                print("Status not found")
                return False

    print("Title not found.")
    return False



title = "The Portable Kipling"
url = "https://kcls.bibliocommons.com/v2/search?query=iron%20widow&searchType=smart"

print(get_kcls_availability(title, url))