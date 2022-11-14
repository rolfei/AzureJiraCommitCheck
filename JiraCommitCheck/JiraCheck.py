import logging
import json
import re
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.git.models import GitPullRequestStatus,GitStatusContext
import azure.functions as func
from azure.devops.exceptions import AzureDevOpsServiceError

class JiraCheck:

    def azureConnect(self,personal_access_token, organization_url):
        # Create a connection to the org
        credentials = BasicAuthentication('', personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)
        git_client= connection.clients_v6_0.get_git_client()

        return git_client

    def get_pr_commit_comments(self,git_client,repository_id,pr_id, project):
        try:
            commits=git_client.get_pull_request_commits(repository_id, pr_id, project=project, top=None, continuation_token=None)
            #print (commits.value[0].comment)
            return commits
        except AzureDevOpsServiceError as ade:
            logging.info('AzureDevOpsServiceError getting pr commits' + str(ade))
            return []

    def validate_comments(self,comments_list):
        pattern = re.compile('(^[A-Z]{2,4}-[0-9]{1,5}) +(.*)')
        for git_commit in comments_list:
            match = pattern.search(git_commit.comment)
            if match:
                return (True,'')
        return (False,'no comment match')

    def check_status(self,git_client,repository_id,pr_id,project):
        try:
            statuses=git_client.get_pull_request_statuses(repository_id, pr_id, project=project)
            if statuses:
                return True
            else:
                return False
        except AzureDevOpsServiceError as ade:
            logging.info('AzureDevOpsServiceError checking status' + str(ade))
            return False

    def delete_status(self,git_client,repository_id,pr_id,project,status_id):
        git_client.delete_pull_request_status(repository_id,pr_id,status_id, project)


    def create_status(self,git_client,repository_id,pr_id,project):
        context=GitStatusContext('JiraCheck', 'JiraCheckPassStatus')
        status=GitPullRequestStatus(context=context,state='succeeded')

        #catch AzureDevOpsServiceError
        git_client.create_pull_request_status( status, repository_id, pr_id, project=project)

    def __init__(self):
        self
