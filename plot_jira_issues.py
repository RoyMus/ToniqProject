import matplotlib.pyplot as plt
from constants import JIRA_API_KEY, JIRA_URL,JIRA_USERNAME,JIRA_PROJECT_KEY
import aiohttp
from aiohttp import BasicAuth
import re
import asyncio

SERVER_REGEX = r'srv-\S+'

auth = BasicAuth(JIRA_USERNAME, JIRA_API_KEY)
headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}

async def fetch_all_issues(jql=f"project={JIRA_PROJECT_KEY}"):
    all_issues = []
    next_page_token = ""
    max_results = 10  
    async with aiohttp.ClientSession() as session:
        params = {
            "jql": jql,
            "nextPageToken" : next_page_token,
            "maxResults": max_results,
            "fields": "summary,description",
        }
        while True:
            params["nextPageToken"] = next_page_token
            async with session.get(f"{JIRA_URL}/rest/api/3/search/jql", params=params, headers=headers, auth=auth) as response:
                    data = await response.json()
                    issues = data.get("issues", [])
                    all_issues.extend(issues)
                    if "nextPageToken" not in data:
                        break  # fetched all issues
                    next_page_token = data["nextPageToken"]
    return all_issues

all_issues = asyncio.run(fetch_all_issues())


tickets_per_server = {"missing_server_issues":0}

for issue in all_issues:
    description_content = issue["fields"]["description"]["content"]
    for paragraph in description_content:
        for paragraph in paragraph["content"]:
            description = paragraph["text"]
            matches = re.findall(SERVER_REGEX, description, re.IGNORECASE)
            if not matches:
                tickets_per_server["missing_server_issues"] += 1
                continue
            for match in matches:
                server_name = match.split("-")
                if len(server_name) > 1:
                    server_name = f"srv-{server_name[1]}"
                else:
                    tickets_per_server["missing_server_issues"] += 1
                    continue
                if server_name not in tickets_per_server:
                    tickets_per_server[server_name] = 0
                tickets_per_server[server_name] += 1
           


# Plotting the server data
servers = list(tickets_per_server.keys())
number_of_tickets = list(tickets_per_server.values())

plt.figure(figsize=(8, 6))
plt.bar(servers, number_of_tickets)

plt.xlabel('Server Name')
plt.ylabel('Num Tickets')
plt.title('Jira Server Issues Counter')

plt.show()