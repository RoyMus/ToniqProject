Please note that I have used the new Jira REST API Doc.

https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-get

According to that documentation GET rest/api/3/search is deprecated so I used rest/api/3/search/jql which doesn't include startAt anymore. (Not updated in most LLMs). It instead uses a nextPageToken which doesn't appear if it's the last page.

Regarding the mission 

- create_jira_issues.py - creates the environment by randomizing many issues. This is Phase 1.
- plot_jira_issues.py - implements Phase 2. The end result is two figures with histograms counting the number of tickets for each technology and each server
- tech_category_classifier.py is a custom module I had built to help me identify the technical keywords and the underlying technology. It is used inisde plot_jira_issues to classify which technology was used
