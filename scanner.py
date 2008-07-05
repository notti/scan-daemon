#!/usr/bin/python

import signal, os, sys, threading, subprocess, stat
import pwd, grp
import ConfigParser

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
except:
    print """Config error. Need at least a "scanner", "destination", "uid" and "gid" in the [Default] Section!"""
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

# Create Directory for the communication socket and set rights

try:
    os.makedirs("/var/run/scanner/")
except OSError, (errno, strerror):
    if errno != 17:
        raise
os.chown("/var/run/scanner",config.uid, config.gid)
os.chmod("/var/run/scanner",stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
try:
    os.unlink("/var/run/scanner/socket.sock")
except:
    pass

os.setgid(config.gid)
os.setuid(config.uid)

# OK - so lets fork the main program which handles signals and spawns the necessary threads

if os.fork() == 0:
   print "ok!" 

