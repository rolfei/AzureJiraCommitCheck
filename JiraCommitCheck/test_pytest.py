import JiraCommitCheck.JiraCheck as JiraCheck

def test_validate_comments():
    jc=JiraCheck.JiraCheck()
    obj = type('', (object,),{"comment": "JIRA-1234 a comment"})()
    comlist=[]
    comlist.append(obj)

    result=jc.validate_comments(comlist)
    assert result==(True,'')
