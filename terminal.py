# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import subprocess
import re
import atexit

def parseArguments():
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument('-s', '--server', required=True, help='mainframe hostname')
    argumentParser.add_argument('-u', '--username', required=True, help='authorization username')
    argumentParser.add_argument('-p', '--password', required=True, help='authorization password')

    return argumentParser.parse_known_args()

def setupLogger():
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(msecs)03d %(message)s', '%H:%M:%S')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger

def log(message):
    logger.info(message)

def readLine():
    global line
    line = process.stdout.readline().rstrip()
    return line

def write(command, *parameters):
    parameters = ','.join(['"%s"' % str(parameter) for parameter in parameters])
    process.stdin.write('%s(%s)\n' % (command, parameters))

    global lines
    lines = []

    while True:
        match = re.match(r'data: ?(?P<line>.*)', readLine())
        if not match:
            break
        lines.append(match.group('line'))
    
    status = line
    result = readLine()

def execute(command, *parameters):
    write(command, *parameters)
    write('Ascii')

def waitForField(timeout=1000):
    execute('Wait', timeout, 'InputField')

def readLines():
    write('Ascii')
    return lines

def readContent():
    return '\n'.join(readLines())

def getField(row, column, length):
    return lines[row - 1][column - 1 : column - 1 + length]

def insertString(string):
    waitForField()
    execute('String', string)

def enter():
    waitForField()
    execute('Enter')

def enterString(string):
    insertString(string)
    enter()

def waitForString(pattern):
    while not re.search(pattern, readContent()):
        enter()

def connect(hostname):
    log("connecting to '%s' host" % hostname)
    execute('Connect', hostname)

def logon(username, password):
    log("logging on as '%s' user" % username)
    enterString('LOGON ' + username)
    enterString(password)

def purgeTerminalJob():
    log('starting SDSF')
    enterString('START S.ST')
    log('filtering jobs')
    enterString('FILTER JOBN EQ ' + username)
    moveCursor(5, 2)
    log('purging terminal job')
    enterString('P')
    
def moveCursor(row, column):
    execute('MoveCursor', row - 1, column - 1)

def executePF(number):
    execute('PF', number)

def waitForISPF():
    log('waiting for ISPF')
    enter()
    waitForString('ISPF Primary Option Menu')

def initializeModule():
    arguments, parameters = parseArguments()

    global hostname
    hostname = arguments.server
    global username
    username = arguments.username
    password = arguments.password

    global logger
    logger = setupLogger()

    if sys.platform == 'linux2':
        program = 's3270'
    elif sys.platform in ['win32', 'cygwin']:
        program = 'ws3270.exe'

    PIPE = subprocess.PIPE
    parameters = [program, '-utf8', '-xrm', 's3270.m3279: True'] + parameters
    global process
    process = subprocess.Popen(parameters, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    connect(hostname)
    logon(username, password)
    waitForISPF()
    atexit.register(purgeTerminalJob)

initializeModule()
