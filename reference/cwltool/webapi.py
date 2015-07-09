#!/usr/bin/env python
from bottle import route,run,get,post,request,response,redirect,HTTPError
from urlparse import urlparse
from uuid import uuid4,UUID
import os,os.path
import tempfile
import main
from StringIO import StringIO


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
    <address>
    <p>Specifications: <a href="https://w3id.org/cwl/draft-2/">Common Workflow Language, draft-2</a></p>
    <p>Source: <a href="https://github.com/common-workflow-language/common-workflow-language/tree/master/reference">github.com/common-workflow-language</a></p>
    </address>
    </div>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.js"></script>

</body>
</html>
"""

def directory_for_uuid(uuid):
    return os.path.join(tempfile.gettempdir(), str(uuid), "")

MASTER_WORKFLOW="_workflow.cwl"

@post("/cwl")
def cwl():
    url = request.forms.get("url")
    if url:
        return redirect("cwl/%s" % url)

    uuid = str(uuid4())
    directory = directory_for_uuid(uuid)
    os.mkdir(directory)
    print "Storing in", directory
    first = None
    for upload in request.files.getlist("upload"):
        print upload.filename
        if first is None:
            first = upload.filename
        raw = upload.raw_filename
        # TODO: Mapping to handle 'nasty' raw filenames
        upload.save(directory)

    # TODO: Properly determine master workflow
    if not first:
        raise HTTPError(400, "No files uploaded")

    os.symlink(os.path.join(directory, first),
               os.path.join(directory, MASTER_WORKFLOW))
    return redirect("cwl/%s" % uuid)

def is_absolute(url):
    u = urlparse(url)
    if u.scheme in ("http", "https"):
        return True
    return False

def url_location(url):
    print "Checking", url
    try:
        uuid = UUID(url)
        if uuid.version==4:
            print "It's a uuid"
            directory = directory_for_uuid(uuid)
            # TODO: Check if directory exists and raise 410
            return directory
    except ValueError:
        pass

    # Not a UUID? then it should be an absolute htttp(s) URL
    if not is_absolute(url):
        raise HTTPError(403, "Unsupported URL: " + url)
    # TODO: Block localhost, 0.0.0.0, 127.0.0.1, 10.x.x.x, etc. etc. etc...
    # Don't forget IPV6!
    return url

#get("/cwl") # TODO: Handle ?url=
@get("/cwl/<url:path>")
def cwl(url):
    if (request.query_string):
        url = url + "?" + request.query_string
    loc = url_location(url)
    args = ["--print-rdf"]
    if not is_absolute(url):
        args.append("--basedir")
        args.append(loc)
        loc = os.path.join(loc, MASTER_WORKFLOW)
    args.append(loc)

    output = StringIO()
    status = main.main(args, output=output)
    if status == 0:
        response.add_header("Content-Type", "text/turtle")
        return output.getvalue()

    raise HTTPError(500, "Status: %s\nOutput: %s" % (status, output.getvalue()))

if __name__=="__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
