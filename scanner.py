#!/usr/bin/python

import signal, os, sys, threading, subprocess, stat
import pwd, grp
import ConfigParser
import control, scanners, http

# -=-=-=-=-=- READ CONFIG -=-=-=-=-=-=-
class cfg:
    pass

config = cfg()
config.parser = ConfigParser.ConfigParser()
config.parser.read(['scanner.cfg','/etc/scanner.cfg'])

try:
    config.scanner      = config.parser.get('Default','scanner')
    config.uid          = config.parser.get('Default','uid')
    config.gid          = config.parser.get('Default','gid')
    config.destination  = config.parser.get('Default', 'destination')
    config.socket       = config.parser.get('Default', 'socket')
    config.port         = config.parser.getint('Default', 'port')
except:
    print """Config error. Need at least a "scanner", "destination", "uid", "gid", "socket" and "port" in the [Default] Section!"""
    exit(os.EX_CONFIG)
config.num_worker_threads = config.parser.getint('Default','worker_threads')
config.default_dct_quality = config.parser.getint('Default','dct_quality')
config.default_flatecompresslevel = config.parser.getint('Default','flatecompresslevel')
try:
    config.num_worker_threads = config.parser.getint('Default','worker_threads')
    config.default_dct_quality = config.parser.getint('Default','dct_quality')
    config.default_flatecompresslevel = config.parser.getint('Default','flatecompresslevel')
except:
    pass

if config.uid.isdigit():
    config.uid = int(config.uid)
else:
    config.uid = pwd.getpwnam(config.uid)[2]
if config.gid.isdigit():
    config.gid = int(config.gid)
else:
    config.gid = grp.getgrnam(config.gid)[2]

scanner_list = {}
for scanner in config.scanner.split(','):
    scanner = scanner.strip()
    scanner_list[scanner] = scanners.scanners[scanner](config)
notify = control.control(config, scanner_list)

webserver = http.http(config, scanner_list)

os.setgid(config.gid)
os.setuid(config.uid)

# OK - so lets fork the main program which handles signals and spawns the necessary threads

if os.fork() == 0:
    t = threading.Thread(target = notify.serve_forever)
    t.setDaemon(True)
    t.start()
    t = threading.Thread(target = webserver.serve_forever)
    t.setDaemon(True)
    t.start()
    for name, scanner in scanner_list.iteritems():
        t = threading.Thread(target = scanner.serve_forever)
        t.setDaemon(True)
        t.start()
    
    signal.pause()

