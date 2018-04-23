from flask import Flask, abort, render_template, request, send_file
import configparser
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from otsrdflib import OrderedTurtleSerializer
from rfc3987 import match
import time
import posixpath
import logging as log
from urllib.parse import quote_plus, unquote_plus
import io
from turtlegit.cmdgit import status, size, lsfiles, add, commit, loglast, diffnoindex, hist, branchlist, checkout
import pkg_resources
import stat
import os
from os import path, remove, makedirs, chmod, system
from turtlegit.filegraph import FileGraph
from turtlegit.default_settings import Config, Logging
import shutil
import whatthepatch

app = Flask(__name__)

# TODO: Load workspace from env param?
def getWorkspacePath():
    return posixpath.join(Config.ROOT_DIR, 'workspace')

domain = Config.DOMAIN
workspace = getWorkspacePath()
autoadd = Config.AUTOADD
autocommit = Config.AUTOCOMMIT

def init():
    #TODO: Read settings?
    #config = configparser.ConfigParser()
    #config.read('settings.ini')
    log.basicConfig(level=log.getLevelName(Logging.LEVEL))
    
init()

@app.route("/", methods=['GET'])
def hello():
    return render_template('help.html')

@app.route("/<repo>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def run(repo):
    
    log.info("Request to: "+request.base_url)
    log.info("workspace:"+workspace)
    repopath = posixpath.join(workspace, repo)
    
    log.info("repopath:"+repopath)
    
    log.info("Running "+repo+" repository in "+workspace)
    log.info(repopath)

    if not status(repopath):
        log.debug("Repository "+repo+" doesnt exist in "+repopath)
        abort(404)
    else:
        log.info("Repository size: "+size(repopath))
    
    graph = request.args.get('graph','')
    branch = request.args.get('branch','')
    checkoutBranch(branch, repopath)
    
    if graph == "":
        filelist = lsfiles(repopath)
        return render_template('list.html',data=pathsToURIs(repo, filelist));
    elif not match(graph,rule='absolute_IRI'):
        log.debug("Graph URI is not valid")
        abort(406)
    
    if notSupportedContentType(request):
        abort(412)
            
    fileGraph = FileGraph(graph, domain, repopath, repo)
           
    if request.method == 'GET':
        if fileGraph.doExists():
            return send_file(fileGraph.filepath,'text/turtle')
        else:
            abort(404)
    elif request.method == 'POST':
        #TODO: Abort on history branches. Create list of actual branches?
        log.debug("POST to "+fileGraph.iri)
        if fileGraph.doExists():
            fileGraph.parsePath()
        fileGraph.parseString(request.data.decode('utf-8'))
        fileGraph.serialize()
        autoAddAndCommit(fileGraph, "POST - Adding graph "+fileGraph.iri)
        return loglast(repopath)
    elif request.method == 'PUT':
        #TODO: Abort on history branches
        log.debug("PUT to "+fileGraph.iri)
        fileGraph.parseString(request.data.decode('utf-8'))
        fileGraph.serialize()
        autoAddAndCommit(fileGraph, "PUT - Writing graph "+fileGraph.iri)
        return loglast(repopath)
    elif request.method == 'DELETE':
        #TODO: Abort on history branches
        log.debug("DELETE to "+fileGraph.iri)
        if fileGraph.doExists():
            deleteFile(fileGraph.filepath)
            autoAddAndCommit(fileGraph, "DELETE - Removing graph "+fileGraph.iri)
            return ('', 204)
        else:
            log.debug("GRAPH "+fileGraph.iri+" DOES NOT EXIST in "+fileGraph.filepath)
            abort(404)
    else:
        abort(406)    
        
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'ttl'

@app.route('/<repo>/history', methods=['GET'])
def history(repo):
    repopath = path.join(workspace, repo)
    return hist(repopath)

@app.route('/<repo>/branch', methods=['GET'])
def branch(repo):
    repopath = path.join(workspace, repo)
    return branchlist(repopath)

@app.route('/<repo>/diff', methods=['GET'])
def diff(repo):
    repopath = posixpath.join(workspace, repo)
    branch = request.args.get('branch','')
    checkoutBranch(branch, repopath)
    if request.method == 'GET':
        graph1 = request.args.get('a','')
        graph2 = request.args.get('b','')
        fileGraph1 = FileGraph(graph1, domain, repopath, repo)
        fileGraph2 = FileGraph(graph2, domain, repopath, repo)
        log.info(fileGraph1.filename)
        log.info(fileGraph2.filename)
        patchtext = diffnoindex(fileGraph1.filename, fileGraph2.filename, repopath)
        # WTF tuple-structure in wthatthepatch
        # https://pypi.org/project/whatthepatch/
        patch = list(whatthepatch.parse_patch(patchtext))[0][1]
        log.info(patchtext)
        for diff in patch:
            a,b,line = diff
            if(b==None):
                print("In a, not in b: "+line)
            if(a==None):
                print("In b, not in a: "+line)
        #TODO: Do something with this ... huh?
        return patchtext
    
##TODO: Create better templated
@app.route('/<repo>/upload', methods=['GET', 'POST'])
def upload_file(repo):
    repopath = posixpath.join(workspace, repo)
    branch = request.args.get('branch','')
    checkoutBranch(branch, repopath)    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            log.info("No file")
            abort(501)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            log.info("No filename?")
            abort(501)
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            fileUri = domain+repo+"/"+file.filename
            fileGraph = FileGraph(fileUri, domain, repopath, repo)
            fileGraph.parseFile(file)
            fileGraph.serialize()
            autoAddAndCommit(fileGraph, "Uploaded file: "+fileGraph.iri)
            return ('',200)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''        

def checkoutBranch(branch, repopath):
    if branch != "":
        checkout(branch, repopath)
    else:
        branch="master"
        checkout(branch, repopath)
        
def autoAddAndCommit(fileGraph, message):
    if autoadd:
        add(fileGraph.filename, fileGraph.repopath)
    if autocommit:
        commit(message, fileGraph.repopath)
    
def pathsToURIs(service, files):
    for n, i in enumerate(files):
        if unquote_plus(i).startswith("http://"):
            files[n] = unquote_plus(path.splitext(i)[0])
        else:
            files[n] = domain+service+'/{0}'.format(quote_plus(path.splitext(i)[0])) 
    return files

def notSupportedContentType(request):
    try:
        if request.headers['Content-Type'] in ['text/turtle','text/html']:
            return False
        else:
            return True
    except KeyError:
            #TODO: Returns with browser but can fail with POST/PUT 
            return False
        
def getDirFromWorkspace(dirName):
    return posixpath.join(getWorkspacePath(),dirName)
    
def createDir(pathToDir):
    if not path.exists(pathToDir):
        makedirs(pathToDir) 
        
def deleteDir(pathToDir):
    if path.exists(pathToDir):
        shutil.rmtree(pathToDir, onerror=remove_readonly)
        
def remove_readonly(func, path, _):
    "Is needed to remove hidden&readonly .git stuff"
    chmod(path, stat.S_IWRITE)
    # Not necessary?
    #if os.name == 'nt':
    #    system("attrib -r -h -s "+name)
    func(path)

def deleteFile(pathToDir):
    remove(pathToDir)   
        
if __name__ == "__main__":
    log.info(workspace)
    app.run(
        port=5000,
        debug=True
    )
    
