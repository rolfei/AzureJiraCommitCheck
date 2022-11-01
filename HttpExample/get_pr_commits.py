from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.models import GitPullRequestStatus,GitStatusContext
import pprint
import re
import requests
import logging
import http.client


http.client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Fill in with your personal access token and org URL
personal_access_token = '<pat_token>'
organization_url = '<org_url>'
repository_id='<repo_id>'
project='<project>'


def azureConnect():
    # Create a connection to the org
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)
    git_client= connection.clients_v6_0.get_git_client()

    return git_client

def get_pr_commit_comments(git_client,pr_id,project):
    commits=git_client.get_pull_request_commits(repository_id, pr_id, project=project, top=None, continuation_token=None)
    #print (commits.value[0].comment)
    return commits

def validate_comments(comments_list):
    pattern = re.compile('(^[A-Z]{2,3}-[0-9]{1,5}) +(.*)')
    for git_commit in comments_list:
        match = pattern.search(git_commit.comment)
        if match:
            return (True,'')
    return (False,git_commit.comment)

def create_status(git_client,pr_id,project):
    context=GitStatusContext('JiraCheck', 'JiraCheckPassStatus')
    status=GitPullRequestStatus(context=context,state='succeeded')

    git_client.create_pull_request_status( status, repository_id, pr_id, project=project)

def check_status (git_client,pr_id,project):
    statuses=git_client.get_pull_request_statuses(repository_id, pr_id, project=project)
    if statuses:
        return True
    else:
        return False


def delete_status(git_client,pr_id,project,status_id):
    git_client.delete_pull_request_status(repository_id,pr_id,status_id, project)


git_client=azureConnect()
pr_id=5
statuses=check_status(git_client,pr_id,project)
if statuses:
    print("deleting status")
    delete_status(git_client,pr_id,project,1)

comments_list=get_pr_commit_comments(git_client,pr_id,project)
(status,fail_comment)=validate_comments(comments_list)
if status:
    create_status(git_client,pr_id,project)
    print("all commits had jira id")
else:
    print("failed jira validation"+ fail_comment)
