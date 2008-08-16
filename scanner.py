#!/usr/bin/python

import signal, os, sys, threading, subprocess, stat
import pwd, grp
import ConfigParser
import control, device, http
import glob

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

# XXX move to device.py V
devices = []
for device in glob.iglob('devices/*py'):
    try:
        dev = __import__(device[:-3]).devices
    except:
        print "Could not load",device
    else:
        devices += zip(dev.keys(), dev.values())

devices = dict(devices)

scanner_list = {}
for scanner in config.scanner.split(','):
    scanner = scanner.strip()
    scanner_list[scanner] = devices[scanner](config)

# ^ 

notify = control.control(config, scanner_list)

webserver = http.http(config, scanner_list)

os.umask(0077)
os.setgid(config.gid)
os.setuid(config.uid)

# OK - so lets do the double fork magic!
try:
    pid = os.fork()
    if pid > 0:
        os._exit(0)
except OSError, e:
    print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
    sys.exit(1)

#decouple from parent environment
os.chdir("/")
os.setsid()

try:
    pid = os.fork()
    if pid > 0:
        os._exit(0)
except OSError, e:
    print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
    sys.exit(1)

#we don't want to fill anyones terminal with aehh bullshit
si = file('/dev/null', 'r')
so = file('/dev/null', 'a+')
se = file('/dev/null', 'a+', 0)
os.dup2(si.fileno(), sys.stdin.fileno())
os.dup2(so.fileno(), sys.stdout.fileno())
os.dup2(se.fileno(), sys.stderr.fileno())

t = threading.Thread(target = notify.serve_forever)
t.setDaemon(True)
t.start()
t = threading.Thread(target = webserver.serve_forever)
t.setDaemon(True)
t.start()
for name, scanner in scanner_list.iteritems():
    t = threading.Thread(target = scanner.serve_forever)
    t.setDaemon(True) #XXX move to device.py so that this one can end itself clean and shiny!
    t.start()

signal.pause()

