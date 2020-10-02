#!/usr/bin/env python3
import json
import math
import logging
from logging import getLogger, StreamHandler, Formatter

dict_path = "dictionary/"

logger = getLogger("Main-Runner").getChild("anylizer")
# --------------------------------
# temporaly logger. Only for debug
def logger_dbg():
    global dict_path
    # dict_path = "../dictionary/"
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


def init():
    # logger_dbg()
    return

def load_config():
    jop = open(dict_path+'config.json')
    return json.load(jop)

def load_file(target):
    jop = open(dict_path+target)
    return json.load(jop)

def score_calc(data, lis, sum_l, c_long):
    for type in data.keys():
        n = data[type]
        data[type] = round((float(data[type])/float(lis[type])*float(sum_l))*10*math.log2(c_long))
        if type == "Mobile":
            data[type] /= 3;
    return data

def analyze(data, c_long):
    init()
    logger.info("Start analyzing package data")
    config = load_config()
    result = {}
    type_count = {}
    type_count_sum = 0
    for file_name in config.keys():
        mode = config[file_name]['match']
        package_list = load_file(file_name)
        for package_name in package_list:
            type_count_sum+=1
            type = package_list[package_name]
            if type not in type_count:
                type_count[type] = 1
            else:
                type_count[type] += 1
            if mode == 'top':
                lis = [s for s in data if s.startswith(package_name)]
                if len(lis) > 0:
                    logger.info("Package found: " + str(package_name))
                    if type not in result:
                        result[type] = 1
                    else:
                        result[type] += 1
            if mode == 'all':
                lis = [s for s in data if package_name in s]
                if len(lis) > 0:
                    logger.info("Package found: " + str(package_name))
                    if type not in result:
                        result[type] = 1
                    else:
                        result[type] += 1
    logger.info("Complete analyzing package data")
    logger.info("Result: "+ str(result))
    logger.info("Start score calculation")
    result_c = score_calc(result, type_count, type_count_sum, c_long)
    logger.info("Complete score calculation")
    logger.info("Result: "+ str(result_c))
    return result_c
