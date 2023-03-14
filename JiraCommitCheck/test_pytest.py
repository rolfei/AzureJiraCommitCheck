import JiraCommitCheck.JiraCheck as JiraCheck
from azure.devops.v6_0.git.git_client import GitClient
from azure.devops.v6_0.git.models import GitCommitRef
from unittest.mock import Mock, patch, MagicMock
from azure.devops.v6_0.git import GitPullRequestStatus

import unittest

class TestGitClient(unittest.TestCase):
    def test_validate_comments(self):
        jc=JiraCheck.JiraCheck()
        obj = type('', (object,),{"comment": "JIRA-1234 a comment"})()
        comlist=[]
        comlist.append(obj)

        result=jc.validate_comments(comlist)
        assert result==(True,'')

    def test_azureConnect(self):
        pat='12323'
        org_url='https://dev.azure.com'
        mock_client= Mock()
        with patch.object(JiraCheck, 'Connection', return_value=mock_client) as mock_conn:
            mock_get_client = Mock (return_value=mock_client)
            jc=JiraCheck.JiraCheck()
            git_client=jc.azureConnect(pat, org_url)
            assert mock_get_client.assert_any_call

    def test_pr_commit_comments(self):
        pat='12323'
        org_url='https://dev.azure.com'


    def test_get_pull_request_statuses(self):
        # create a mock GitClient object and set the return value for get_pull_request_statuses
        client = GitClient('http://test.com')
        status1=GitPullRequestStatus()
        status1.id=1
        status2=GitPullRequestStatus()
        status2.id=2
        client.get_pull_request_statuses = MagicMock(return_value=[status1, status2])

        # call the method and check the return value
        result = client.get_pull_request_statuses(repository_id='my-repo', pull_request_id=123)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[1].id, 2)
