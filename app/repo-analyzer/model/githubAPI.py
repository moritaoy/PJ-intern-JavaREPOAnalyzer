#!/usr/bin/env python3
from github import Github
import os
import sys
import base64
import logging
from logging import getLogger, StreamHandler, Formatter


g = None
c_size = None

logger = getLogger("Main-Runner").getChild("gitAPI")
# --------------------------------
# temporaly logger. Only for debug
def logger_dbg():
    global logger
    logger = getLogger("LogDBG")
    logger.setLevel(logging.DEBUG)
    handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # stream
    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(handler_format)
    # file_handler = FileHandler('', 'a')
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)
    # logger.addHandler(file_handler)
# --------------------------------



# initialize Config
def init():
    # logger_dbg()
    
    try:
        global token, g
        token = os.environ['PJINTERN_GITTOKEN']
    except KeyError:
        print('Error: Set GITHUB TOKEN to the environment variable "PJINTERN_GITTOKEN"', file=sys.stderr)
        raise 
    g = Github(token)
    return

# If not initialized, then call init()
def check_init():
    if g==None:
        init()
    return

# get Repository by repository name
def get_repo(target):
    res=None
    try:
        res = g.get_repo(target)
    except:
        pass
    return res

def parse_base64(content_64):
    content_str = base64.b64decode(content_64).decode()
    res = content_str.splitlines()
    return res

def parse_import(content):
    return content.replace('import', '').replace('static', '').replace(';', '').strip()

def is_import(s):
    return s.lstrip().startswith("import")

# --------------------------------
# Main method, anlyze repository
# target: Repository Name. ex) "userName/repoName"

def analyze_repo(target):
    check_init()
    logger.info("Start anylize repo: "+str(target))
    check_init()
    repo = get_repo(target)
    if repo == None:
        logger.warning("Not found repo: "+str(target))
        return None
    contents = repo.get_contents("")

    logger.info("Start listing *.java files")

    java_list = []
    count = 0
    while contents:
        count += 1
        if count > 3000:
            logger.warning("File search limit reached. Force stop listing")
            break
        if count%100 == 0:
            logger.info("Listing... "+str(count)+" file loaded")
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            if file_content.name.endswith(".java"):
                java_list.append(file_content)
    logger.info("Complete listing: "+str(len(java_list))+" files found")

    logger.info("Start listing package")

    package_set = set([])
    count_l = 0
    total = len(java_list)
    global c_size
    c_size = 0
    while java_list:
        count_l += 1
        if count_l%100==0:
            logger.info("Listing... "+str(count_l)+" / "+str(total)+" file analyzed")
        file_content = None
        try:
            file_content = java_list.pop(0)
            c_size += file_content.size
            contents = parse_base64(file_content.content)[:100]
            contents_f = list(filter(is_import,contents))
            package_list = list(map(parse_import, contents_f))
            package_set |= set(package_list)
        except Exception as e:
            logger.warning("Error {0}".format(str(e.args[0])).encode("utf-8"))
            logger.warning("Exception raised. analyze canceled for this file: "+str(file_content))
            pass
    logger.info("Complete listing package: "+str(len(package_set))+" package found")
    return package_set
    
