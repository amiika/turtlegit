from subprocess import Popen, PIPE
import logging as log
import re

def add(fileName, repoDir):
    log.debug('Adding '+fileName+' to '+repoDir)
    cmd = 'git add ' + fileName
    if not pipeSuccess(cmd, repoDir):
        log.warn('FAILED to add '+fileName+' to '+repoDir)
        
def commit(commitMessage, repoDir):
    log.debug('Committing all to '+repoDir)
    cmd = 'git commit -am "%s"'%commitMessage
    if not pipeSuccess(cmd, repoDir):
        log.warn('FAILED to commit all '+repoDir)
    
def push(repoDir):
    cmd = 'git push '
    if not pipeSuccess(cmd, repoDir):
        log.warn('FAILED to push '+repoDir)
        
def status(repoDir):
    cmd = 'git status '
    return pipeSuccess(cmd, repoDir)

def init(repoDir):
    cmd ='git init '
    return pipeSuccess(cmd, repoDir)

def rmAll(repoDir):
    cmd = 'git rm *'
    return pipeSuccess(cmd,repoDir)

def checkout(branch, repoDir):
    cmd ='git checkout '+branch
    return pipeSuccess(cmd, repoDir)

def pipeSuccess(cmd, repoDir):
    try:
        pipe = Popen(cmd, shell=True, cwd=repoDir,stdout = PIPE,stderr = PIPE)
        (output,error)= pipe.communicate()
        if 'fatal' in error.decode('ascii'):
            log.warn(error)
        log.info(output)
    except (OSError, NotADirectoryError) as exception:
        log.warn('Exception: ' + str(exception))
    else:
        return pipe.wait() == 0

def branchlist(repoDir):
    cmd = 'git branch --list'
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('ascii')
    return output

def hist(repoDir):
    cmd = 'git log --oneline --no-decorate'
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('ascii')
    return output

def size(repoDir):
    cmd = 'git count-objects -v -H '
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('ascii')
    size_pack = re.search("(?<=size-pack: )\d+", output).group()
    return size_pack

def modified(repoDir):
    cmd = 'git ls-files -m '
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('ascii')
    return output

def lsfiles(repoDir):
    cmd = 'git ls-files '
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('ascii')
    return output.splitlines()

def loglast(repoDir):
    cmd = 'git log -p -1 '
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('utf-8')
    return output

def diffnoindex(file1, file2, repoDir):
    log.info("TEST")
    cmd = 'git diff --no-index --relative '+file1+' '+file2
    log.info(cmd)
    p = Popen(cmd, shell=True, cwd=repoDir, stdout=PIPE)
    output = p.communicate()[0].decode('utf-8')
    return output

def setHome():
    cmd = 'set HOME='
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0].decode('utf-8')
    return output  

def getHome():
    cmd = 'set HOME'
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0].decode('utf-8')
    return output  
    

        