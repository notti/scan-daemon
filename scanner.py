#!/usr/bin/python

# Copyright (c) 2008 Gernot Vormayr <notti@fet.at>
#
# This file is part of scan-daemon.
# 
# scan-daemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# scan-daemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
import signal, os, sys, threading, syslog
import ConfigParser

# so lets do the double fork magic!
try:
    pid = os.fork()
    if pid > 0:
        os._exit(0)
except OSError, e:
    print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
    sys.exit(1)

#decouple from parent environment
os.chdir(sys.path[0])
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
#se = file('/dev/null', 'a+', 0)
se = file('/var/log/scan_errors','a+',0)
os.dup2(si.fileno(), sys.stdin.fileno())
os.dup2(so.fileno(), sys.stdout.fileno())
os.dup2(se.fileno(), sys.stderr.fileno())

syslog.openlog('scanner',0,syslog.LOG_DAEMON)

# -=-=-=-=-=- READ CONFIG -=-=-=-=-=-=-
class cfg:
    pass

try:
    config = cfg()
    config.parser = ConfigParser.SafeConfigParser()
    config.parser.read(open('defaults.cfg'))
    config.parser.read(['scanner.cfg','/etc/scanner.cfg'])

    config.scanner              = config.parser.get('main','scanner')
    config.uid                  = config.parser.get('main','uid')
    config.gid                  = config.parser.get('main','gid')
    config.destination          = config.parser.get('main', 'destination')
    config.socket               = config.parser.get('main', 'socket')
    config.port                 = config.parser.getint('main', 'port')
    config.num_worker_threads   = config.parser.getint('main','worker_threads')
    config.dct_quality          = config.parser.getint('main','dct_quality')
    config.flatecompresslevel   = config.parser.getint('main','flatecompresslevel')
except ConfigParser.NoSectionError, err:
    syslog.syslog(syslog.LOG_ERR, "No '%s' Section in config file!" % err.section)
    exit(os.EX_CONFIG)
except ConfigParser.NoOptionError, err:
    syslog.syslog(syslog.LOG_ERR, "No '%s' Option in Section '%s' in config file!" % (err.section, err.option))
    exit(os.EX_CONFIG)
except ConfigParser.Error, err:
    syslog.syslog(syslog.LOG_ERR, err)
    exit(os.EX_CONFIG)

#convert uid/gid if needed
if config.uid.isdigit():
    config.uid = int(config.uid)
else:
    import pwd
    config.uid = pwd.getpwnam(config.uid)[2]
if config.gid.isdigit():
    config.gid = int(config.gid)
else:
    import grp
    config.gid = grp.getgrnam(config.gid)[2]

#load all our components
import device
scanners = device.scanners(config)
import control
notify = control.control(config, scanners)
import http
webserver = http.http(config, scanners)

#drop our privileges n stuff
os.umask(0077)
os.setgid(config.gid)
os.setuid(config.uid)

#let's spawn everything we need
t = threading.Thread(target = notify.serve_forever, name = 'Control')
t.setDaemon(True)
t.start()
t = threading.Thread(target = webserver.serve_forever, name = 'Webserver')
t.setDaemon(True)
t.start()

#signal handler
def handler(signum, frame):
    scanners.shutdown()

signal.signal(signal.SIGTERM, handler)

#start up our actual service
scanners.serve_forever()

#this spawns non daemonic threads, so we can finally finish here
syslog.syslog(syslog.LOG_INFO, 'startup complete')

signal.pause()

