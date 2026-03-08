import webbrowser
import urllib.parse


def handle_web(command: str) -> str:
    lower = command.lower()
    
    if lower.startswith("search "):
        query = command[7:].strip()
        if not query:
            return "What do you want to search for?"
        url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
        webbrowser.open(url)
        return f"Searching for {query}"

    parts = lower.replace("open ", "", 1).replace("website ", "", 1).replace("go to ", "", 1).strip().split()
    if not parts:
        return "No website specified."
    site = "".join(parts)
    if "." not in site:
        site = site + ".com"
    if not site.startswith("http"):
        site = "https://" + site
    webbrowser.open(site)
    return "Opening " + site
