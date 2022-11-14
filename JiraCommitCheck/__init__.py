import logging
import json
import azure.functions as func
import JiraCommitCheck.JiraCheck as JiraCheck

# Fill in with your personal access token and org URL
personal_access_token = '<pattoken>'
organization_url = 'https://dev.azure.com/<org>'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python JIRA CHECK trigger function processed a request.')
    jc=JiraCheck.JiraCheck()

    req_body = req.get_json()
    json_object = json.dumps(req_body, indent = 4)

    logging.info('repo id.'+ req_body["resource"]["repository"]["id"] )
    logging.info('project.'+ req_body["resource"]["repository"]["project"]["name"] )
    logging.info('PR id.'+ str(req_body['resource']['pullRequestId']))
    repo_id=req_body["resource"]["repository"]["id"]
    project=req_body["resource"]["repository"]["project"]["name"]
    pr_id=req_body['resource']['pullRequestId']
    git_client=jc.azureConnect(personal_access_token,organization_url)

    statuses=jc.check_status(git_client,repo_id,pr_id,project)
    if statuses:
        logging.info("deleting status")
        jc.delete_status(git_client,repo_id,pr_id,project,1)


    comments_list=jc.get_pr_commit_comments(git_client,repo_id,pr_id,project)
    (status,fail_comment)=jc.validate_comments(comments_list)
    logging.info('validate result'+fail_comment)

    if status:
        jc.create_status(git_client,repo_id,pr_id,project)
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
