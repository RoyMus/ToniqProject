import random 
from aiohttp import BasicAuth
import asyncio
import aiohttp
import json
from constants import JIRA_API_KEY,TECHNOLOGY_TEMPLATES, JIRA_URL,JIRA_USERNAME,JIRA_PROJECT_KEY

NUMBER_OF_ISSUES_TO_CREATE = 20000
MAX_ISSUES_PER_REQUEST = 50
url = f"{JIRA_URL}/rest/api/3/issue/bulk"
servers = ["a","b","c","d"]
server_annotations = ["srv","SRV","Srv"]
dbs = ["users_db","orders_db","payments_db"]
probability_to_ignore_server = 0.1

auth = BasicAuth(JIRA_USERNAME, JIRA_API_KEY)
headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}


def randomize_payload(i):
    random_key = random.choice(list(TECHNOLOGY_TEMPLATES.keys()))
    random_text = random.choice(TECHNOLOGY_TEMPLATES[random_key])
    random_server = f"{random.choice(server_annotations)}-{random.choice(servers) if random.random() > probability_to_ignore_server else ''}" if random.random() > probability_to_ignore_server else ""
    random_server2 = f"{random.choice(server_annotations)}-{random.choice(servers) if random.random() > probability_to_ignore_server else ''}" if random.random() > probability_to_ignore_server else ""
    random_db = random.choice(dbs)
    return {
        "fields": {
        "project":
        {
            "key": JIRA_PROJECT_KEY
        },
        "summary": f"Ticket {i + 1}",
        "description": {
            "content": [
                {
                "content": [
                    {
                        "text": random_text.format(server=random_server, server2=random_server2, db_name=random_db),
                        "type": "text"
                    },
                ],
                    "type": "paragraph"
                }
                ],
                    "type": "doc",
                    "version": 1
            },
            "issuetype": {
                "name": "Task"
            }
        }
    }

def chunk_list(items, size=50):
    for i in range(0, len(items), size):
        yield items[i:i + size]

async def bulk_create_issues():
    issues = []
    for i in range(NUMBER_OF_ISSUES_TO_CREATE):
        issues.append(randomize_payload(i))
    async with aiohttp.ClientSession() as session:
        for chunk in chunk_list(issues, MAX_ISSUES_PER_REQUEST):
            payload = {"issueUpdates": chunk}
            async with session.post(url, data=json.dumps(payload), headers=headers, auth=auth) as response:
                print(json.dumps(json.loads(await response.text()), sort_keys=True, indent=4, separators=(",", ": ")))

asyncio.run(bulk_create_issues())