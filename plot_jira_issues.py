import matplotlib.pyplot as plt
from constants import JIRA_API_KEY, JIRA_URL,JIRA_USERNAME,JIRA_PROJECT_KEY
from tech_category_classifier import classify
import aiohttp
from aiohttp import BasicAuth
import re
import asyncio
import json
import os
import sys
import signal

SERVER_REGEX = r'srv-\S+'

auth = BasicAuth(JIRA_USERNAME, JIRA_API_KEY)
headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}
SAVE_FILE = "jira_progress.json"

# Global variable to store data to save
progress_data = {
    "all_issues": [],
    "nextPageToken": ""
}

def save_progress():
    """Saves the current issues and nextPageToken to a JSON file"""
    with open(SAVE_FILE, "w") as f:
        json.dump(progress_data, f)

def handle_exit(signum, frame):
    print(f"Saving progress...")
    save_progress()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # kill command


async def fetch_all_issues(project={JIRA_PROJECT_KEY}):
    global progress_data

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            progress_data = json.load(f)
            print(f"Loaded progress from {SAVE_FILE} with next_page_token {progress_data.get('nextPageToken', '')}")
            
    all_issues = progress_data.get("all_issues", [])
    next_page_token = progress_data.get("nextPageToken", "")
    max_results = 10  
    max_pages = 10000
    page_counter = 0

    async with aiohttp.ClientSession() as session:
        params = {
            "jql": f"project={project}",
            "nextPageToken" : next_page_token,
            "maxResults": max_results,
            "fields": "summary,description",
        }
        while page_counter < max_pages:
            params["nextPageToken"] = next_page_token
            async with session.get(f"{JIRA_URL}/rest/api/3/search/jql", params=params, headers=headers, auth=auth) as response:
                    data = await response.json()
                    issues = data.get("issues", [])
                    all_issues.extend(issues)
                    progress_data["all_issues"] = all_issues
                    progress_data["nextPageToken"] = data.get("nextPageToken", "")
                    save_progress()
                    if "nextPageToken" not in data or not issues:
                        break  # fetched all issues
                    next_page_token = data["nextPageToken"]
                    page_counter += 1
    return all_issues

all_issues = asyncio.run(fetch_all_issues())

def count_tickets_per_category(all_issues):
    tickets_per_server = {"unrecognized_server_issues":0}
    tickets_per_technology = {"unknown":0}

    for issue in all_issues:
        description_content = issue["fields"]["description"]["content"]
        for paragraph in description_content:
            for paragraph in paragraph["content"]:
                description = paragraph["text"]

                tech_category = classify(description)
                if tech_category not in tickets_per_technology:
                    tickets_per_technology[tech_category] = 0
                tickets_per_technology[tech_category] += 1

                matches = re.findall(SERVER_REGEX, description, re.IGNORECASE)
                if not matches:
                    tickets_per_server["unrecognized_server_issues"] += 1
                    continue
                for match in matches:
                    server_name = match.split("-")
                    if len(server_name) > 1:
                        server_name = f"srv-{server_name[1]}"
                    else:
                        tickets_per_server["unrecognized_server_issues"] += 1
                        continue
                    if server_name not in tickets_per_server:
                        tickets_per_server[server_name] = 0
                    tickets_per_server[server_name] += 1
    return tickets_per_server, tickets_per_technology


tickets_per_server, tickets_per_technology = count_tickets_per_category(all_issues)


# Plotting the server data
servers = list(tickets_per_server.keys())
number_of_tickets = list(tickets_per_server.values())

plt.figure(1,figsize=(9, 6))
plt.bar(servers, number_of_tickets)

plt.xlabel('Server Name')
plt.ylabel('Num Tickets')
plt.title('Jira Server Issues Counter')

# Plotting the technology data
tech_used = list(tickets_per_technology.keys())
number_of_tickets = list(tickets_per_technology.values())

plt.figure(2,figsize=(8, 6))
plt.bar(tech_used, number_of_tickets)

plt.xlabel('Technology')
plt.ylabel('Num Tickets')
plt.title('Jira Technology Issues Counter')

plt.show()