import logging
import json
import re
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.models import GitPullRequestStatus,GitStatusContext
import azure.functions as func

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

def get_pr_commit_comments(git_client,pr_id):
    commits=git_client.get_pull_request_commits(repository_id, pr_id, project='HomeManager', top=None, continuation_token=None)
    #print (commits.value[0].comment)
    return commits

def validate_comments(comments_list):
    pattern = re.compile('(^[A-Z]{2,3}-[0-9]{1,5}) +(.*)')
    for git_commit in comments_list:
        match = pattern.search(git_commit.comment)
        if match:
            return (True,'')
    return (False,'no comment match')

def check_status (git_client,pr_id,project):
    statuses=git_client.get_pull_request_statuses(repository_id, pr_id, project=project)
    if statuses:
        return True
    else:
        return False

def delete_status(git_client,pr_id,project,status_id):
    git_client.delete_pull_request_status(repository_id,pr_id,status_id, project)


def create_status(git_client,pr_id):
    context=GitStatusContext('JiraCheck', 'JiraCheckPassStatus')
    status=GitPullRequestStatus(context=context,state='succeeded')

    #catch AzureDevOpsServiceError
    git_client.create_pull_request_status( status, repository_id, pr_id, project=project)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python JIRA CHECK trigger function processed a request.')


    req_body = req.get_json()
    json_object = json.dumps(req_body, indent = 4)

    logging.info('repo id.'+ req_body["resource"]["repository"]["id"] )
    logging.info('PR id.'+ str(req_body['resource']['pullRequestId']))
    pr_id=req_body['resource']['pullRequestId']
    git_client=azureConnect()

    statuses=check_status(git_client,pr_id,project)
    if statuses:
        logging.info("deleting status")
        delete_status(git_client,pr_id,project,1)


    comments_list=get_pr_commit_comments(git_client,pr_id)
    (status,fail_comment)=validate_comments(comments_list)
    logging.info('validate result'+fail_comment)

    if status:
        create_status(git_client,pr_id)
        logging.info("all commits had jira id")
        return func.HttpResponse(
            "SUCCESS Comment match JIRA:"+req_body["detailedMessage"]["text"],
           #  "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."+json_object ,
             status_code=200
        )
    else:
        logging.info("pull request had commits missing jira id")
        return func.HttpResponse(
            "FAIL NO JIRA Comment:"+req_body["detailedMessage"]["text"],
           #  "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."+json_object ,
             status_code=422
        )

#https://dev.azure.com//ianerolfe/HomeManager/_apis/git/repositories/3c16acf8-27e8-4950-ab65-f5e64300efe0/pullRequests/1/commits?api-version=6.0
