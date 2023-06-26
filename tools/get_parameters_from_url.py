import re

search_url = "https://www.google.com/search?q=pizza+hut+new+york&oq=pizza+hut+new+york&aqs=chrome..69i57j0i67i131i433i512l2j0i131i433i512j0i131i433i512l2.5515j1j7&sourceid=chrome&ie=UTF-8"

pattern = r"https://www.google.com/search\?q=([^&]+)&oq=([^&]+)&aqs=([^&]+)&sourceid=([^&]+)&ie=([^&]+)"

match = re.search(pattern, search_url)

if match:
    q = match.group(1)
    oq = match.group(2)
    aqs = match.group(3)
    sourceid = match.group(4)
    ie = match.group(5)
    print(f"q={q}, oq={oq}, aqs={aqs}, sourceid={sourceid}, ie={ie}")
else:
    print("No match found.")
