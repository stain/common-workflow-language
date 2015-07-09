#!/usr/bin/env python
from bottle import route,run,get,post,request,response,redirect

@route("/")
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CWL view</title>
    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.css">
    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.css">
</head>
<body>
    <div class="container">
        <h1>CWLview</h1>
        <h2>Inspect Common Workflow Language workflows</h2>
        <div class="jumbotron">
            Upload CWL file(s):
            <form role="form" action="cwl" method="POST" enctype="multipart/form-data">
            <div>
                <input name="upload" type="file" multiple="multiple" accept="text/yaml,.yaml,.yml,.cwl"/>
                </div>
                -or-
                <div>
                <input name="url" type="url" class="form-control" placeholder="http://example.com/workflow.cwl" />
                </div>
                <div>
                <input type="submit" class="btn btn-primary btn-lg" value="Visualize" />
                </div>
            </form>
        </div>
    </div>
    <address>
    Specifications: <a href="https://w3id.org/cwl/draft-2/">Common Workflow Language, draft-2</a>
    </address>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.js"></script>

</body>
</html>
"""

@get("/cwl/<url:path>")
@post("/cwl")
def cwl(upload=[], url=None):
    upload = request.files.get('upload')
    return "Hello %s" % upload

if __name__=="__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
