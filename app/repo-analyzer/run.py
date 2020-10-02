#!/usr/bin/env python3
import json
import boto3
import logging
import traceback
import time
from logging import getLogger, StreamHandler, Formatter

import model.analyze_package as analyzer
import model.githubAPI as git
logger = None

def init():
    global logger
    logger = getLogger("Main-Runner")
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

    global sqs,sqs_url
    sqs = boto3.client('sqs')
    sqs_url = 'https://sqs.ap-northeast-1.amazonaws.com/433403878829/pj-intern-analyze-queue'

    global dynamodb, repo_table
    dynamodb = boto3.resource('dynamodb')
    repo_table = dynamodb.Table('pj-intern-repo-data')
    

def analyze(target):
    if logger == None:
        init()
    data = git.analyze_repo(target)
    if data == None:
        logger.warning("Repository not Found. Cancel analyze")
        return None
    size = git.c_size
    res = analyzer.analyze(data,size)
    return res

def poll_data():
    response = sqs.receive_message(
        QueueUrl=sqs_url,
        MaxNumberOfMessages=1,
    )
    if 'Messages' not in response:
        return None
    message = json.loads(response['Messages'][0]['Body'])
    return [message,response['Messages'][0]['ReceiptHandle']]

def sqs_del(id,target_sqs):
    sqs.delete_message(QueueUrl=target_sqs,ReceiptHandle=id)
    return

def store_data(data, userId, repoName):
    now = int(time.time())
    item={
        'userId': userId,
        'repoName': repoName,
        'time_update': now,
        'data': json.dumps(data),
        'analyzing': False
    }
    repo_table.put_item(Item=item)

def main():
    init()
    data = None
    logger.info("start polling")
    while True:
        try:
            res = poll_data()
            if res == None:
                continue
            logger.info("received data")
            data = res[0]
            rec = res[1]
            userId = data['userId']
            repo_name = data['repoName']
            target = str(userId)+"/"+str(repo_name)
            
            try:
                logger.info("call analyzer. target: "+target)
                data = analyze(target)
                logger.info("Complete analyze")
                if data != None:
                    store_data(data,userId,repo_name)
            except Exception as e:
                logger.warning("Exception raised while analyzing")
                logger.warning("Error {0}".format(str(e.args[0])).encode("utf-8"))
                # print(traceback.format_exc())
                pass
            
            sqs_del(rec, sqs_url)
        except Exception as e:
            logger.warning("Analyze Fault: data polling or parsing data")
            logger.warning("Error {0}".format(str(e.args[0])).encode("utf-8"))
            # print(traceback.format_exc())
            pass
        logger.info("Finish task")
            
    
if __name__ == "__main__":
    main()
