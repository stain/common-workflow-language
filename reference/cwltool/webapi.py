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
                <button name="dest" value="validate" type="submit" class="btn-success btn-lg">Validate</button>
                <button name="dest" value="rdf" type="submit" class="btn btn-primary btn-lg">RDF Turtle</button>
                <button name="dest" value="rdf;xml" type="submit" class="btn btn-default btn-lg">RDF/XML</button>
                <button name="dest" value="dot" type="submit" class="btn btn-default btn-lg">Graphviz</button>
                <button name="dest" value="dot;svg" type="submit" class="btn btn-default btn-lg">svg</button>
                <button name="dest" value="dot;png" type="submit" class="btn btn-default btn-lg">png</button>
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
    dest = request.forms.get("dest") or "validate"
    url = request.forms.get("url")
    if url:
        return redirect("%s/%s" % (dest,url))

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

    return redirect("%s/%s" % (dest,uuid))

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

def cmd(url, *args):
    # Ensure we always have --dry-run
    args = ["--dry-run"] + list(args)

    if (request.query_string):
        url = url + "?" + request.query_string
    loc = url_location(url)
    base = None
    if not is_absolute(url):
        base = loc
        args.append("--basedir")
        args.append(base)
        loc = os.readlink(os.path.join(loc, MASTER_WORKFLOW))
    args.append(loc)
    output = StringIO()
    status = main.main(args, output=output)
    return (status, output, base)


#get("/cwl") # TODO: Handle ?url=
@get("/rdf;<format>/<url:path>")
@get("/rdf/<url:path>")
def rdf(url, format="turtle"):

    rdf_formats = {
     "turtle": "text/turtle",
     "n3": "text/turtle",
     "xml": "application/rdf+xml",
     "nt": "text/plain"
    }

    (status, output, base) = cmd(url, "--print-rdf", "--rdf-serializer", format)
    if status == 0:
        response.add_header("Content-Type", rdf_formats.get(format, "text/plain"))
        val = output.getvalue()
        if base:
            ## Make it relative again
            ## FIXME: This probably doesn't work well on Windows
            val = val.replace("file://" + base, "")
        return val

    raise HTTPError(500, "Status: %s\nOutput: %s" % (status, output.getvalue()))

@get("/validate/<url:path>")
def validate(url):
    (status, output, base) = cmd(url, "--verbose")
    if status == 0:
        response.add_header("Content-Type", rdf_formats.get(format, "text/plain"))
        return output.getvalue()

    raise HTTPError(500, "Status: %s\nOutput: %s" % (status, output.getvalue()))

@get("/dot;<format>/<url:path>")
@get("/dot/<url:path>")
def dot(url, format="dot"):

    formats = {
        "png": "image/png",
        "svg": "image/svg+xml",
        "ps": "application/postscript",
        "pdf": "application/pdf"
    }

    (status, output, base) = cmd(url, "--print-dot")
    if status == 0:
        if (format=="dot"):
            response.add_header("Content-Type", rdf_formats.get(format, "text/plain"))
            return output.getvalue()


    raise HTTPError(500, "Status: %s\nOutput: %s" % (status, output.getvalue()))


if __name__=="__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
