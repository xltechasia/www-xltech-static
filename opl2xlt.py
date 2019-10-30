#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opl2xlt
-------

@author: astro7467
"""

import configparser, glob, locale, logging, os, platform, re, shutil, sys, subprocess, time
from argparse import ArgumentParser

# Constants
currentDir = os.path.dirname( os.path.realpath(__file__))

# Initialise
totalWarnings = totalErrors = totalProcessed = totalSkipped = 0

# Fetch System Encoding
systemEncoding = locale.getpreferredencoding()
if "ascii" in systemEncoding.lower(): systemEncoding = "UTF-8"

# Custom configparser
class CustomParser(configparser.ConfigParser):
	def safeget(self, section, option, default=None):
		try: return configparser.configparser.get(self, section, option)
		except: return default

	def safegetboolean(self, section, option, default=False):
		try: return configparser.configparser.getboolean(self, section, option)
		except: return default

	def safegetlist(self, section, option, default=[]):
		try: return [item.strip() for item in configparser.configparser.get(self, section, option).split(",")]
		except: return default

	def removeUnset(self):
		# Remove unset options
		for section in self.sections():
			for option, value in self.items(section):
				if value == "": self.remove_option(section, option)

# Fetch config defaults
config = CustomParser()
config.read(os.path.join( currentDir, "opl2xlt.ini"))
osDefaults = os.path.join( currentDir, "opl2xlt-%s.ini" % platform.system().lower())
if os.path.exists( osDefaults): config.read( osDefaults)
config.removeUnset()

# Create Parser to parse the required arguments
parser = ArgumentParser( description="Convert Open Practices Library from CC HUGO GitHUb repository to XLTech Documents Layout (Acedemic Theme)")

# Add arguments for log setting
group = parser.add_mutually_exclusive_group(required=not config.has_option("global", "log"))
group.add_argument( "-l", "--log", default=config.safeget("global", "log"), const=config.safeget("global", "log", os.path.join(currentDir, "opl2xlt.log")), nargs="?", action="store", help="Log to file in addition to STDOUT and STDERR.", dest="log")
group.add_argument( "--no-log", action="store_false", dest="log")

# Add arguments for debug setting
group = parser.add_mutually_exclusive_group(required=not config.has_option("global", "debug"))
group.add_argument( "-g", "--debug", default=config.safegetboolean("global", "debug", False), action="store_true", help="Enable debug logging", dest="debug")
group.add_argument( "--no-debug", action="store_false", dest="debug")

# Add arguments to enable dry run
group = parser.add_mutually_exclusive_group(required=not config.has_option("global", "dry_run"))
group.add_argument( "-y", "--dry-run", default=config.safegetboolean("global", "dry_run", False), action="store_true", help="Enable dry run for testing", dest="dry_run")
group.add_argument( "--no-dry-run", action="store_false", dest="dry_run")

# Add arguments to enable or disable preserving of timestamp
group = parser.add_mutually_exclusive_group(required=not config.has_option("global", "preserve_timestamp"))
group.add_argument( "-p", "--preserve-timestamp", default=config.safegetboolean("global", "preserve_timestamp", True), action="store_true", help="Preserve timestamp of source files", dest="preserve_timestamp")
group.add_argument( "--no-preserve-timestamp", action="store_false", dest="preserve_timestamp")

# Add arguments for binary locations
binarys = parser.add_argument_group("binarys")
binarys.add_argument( "--git", default=config.safeget("global", "git"), action="store", required=not config.has_option("global", "git"), help="Path to git binary.", dest="git_bin")

# Add arguments for directory locations
folders = parser.add_argument_group("folders")
folders.add_argument( "-d", "--dir", "--dest", "--www", default=None, action="store", help="Location of folder for XLTech WWWW Static files", dest="dest")
folders.add_argument( "-s", "--src", "--source", default=None, action="store", help="Source folder for Open Practice Library files", dest="src")
folders.add_argument( "--sub", "--opl", default=None, action="store", help="Sub directory or folder in XLtech structure e.g. /opl or docs/opl", dest="oplsub")

# Parse All Args
args = parser.parse_args()

# Create class to filter logger to Debug and Info logging
class InfoFilter(logging.Filter):
	def filter(self, rec):
		logLevel = rec.levelno
		if logLevel == logging.ERROR:
			global totalErrors
			totalErrors += 1
		elif logLevel == logging.WARNING:
			global totalWarnings
			totalWarnings += 1
		return logLevel in (logging.DEBUG, logging.INFO)

# Create logger file
logger = logging.getLogger("opl2xlt")
logger.setLevel(logging.DEBUG)

# Create formatter Object
formatter = logging.Formatter("[ %(asctime)s ] %(levelname)-7s --- %(message)s", "%Y-%m-%d %I:%M:%S %p")
cformatter = logging.Formatter("%(levelname)-7s --- %(message)s")

# Create console handler with a log level of debug and info
consoleHandler1Stdout = logging.StreamHandler(sys.stdout)
consoleHandler1Stdout.setLevel(logging.DEBUG if args.debug else logging.INFO)
consoleHandler1Stdout.setFormatter(cformatter)
consoleHandler1Stdout.addFilter(InfoFilter())
logger.addHandler(consoleHandler1Stdout)

# Create console handler with a log level of warning and above
consoleHandlerStderr = logging.StreamHandler(sys.stderr)
consoleHandlerStderr.setLevel(logging.WARNING)
consoleHandlerStderr.setFormatter(cformatter)
logger.addHandler(consoleHandlerStderr)

# Create file handler which logs even debug messages
if args.log:
	if os.path.exists(args.log.encode(systemEncoding)):
		fileHandler = logging.handlers.TimedRotatingFileHandler(args.log.encode(systemEncoding), when="h", interval=1, backupCount=4)
		fileHandler.doRollover()
	else: fileHandler = logging.handlers.TimedRotatingFileHandler(args.log.encode(systemEncoding), when="h", interval=1, backupCount=4)
	fileHandler.setLevel(logging.DEBUG)
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)
	logger.debug("Log file opened at %s", args.log.encode(systemEncoding))

# Loop each argument and log to file
logger.info("=========")
logger.info("Running %s with configuration:", os.path.basename(__file__))
logger.info("=========")
logger.info("SYSTEM_ENCODING = %s" % systemEncoding)

for key, value in vars(args).iteritems():
	# if key == "path": continue
	if isinstance(value, unicode): logger.info("%s = %s", key.upper(), value.encode(systemEncoding))
	else: logger.info("%s = %s", key.upper(), value)

oplDir = os.path.join( os.environ.get( "HOME"), "git/openpracticelibrary")
wwwDir = os.path.join( os.environ.get( "HOME"), "git/www-xltech-static")
wwwOPL = os.path.join( wwwDir, "opl")

try:
  status = os.access( oplDir, os.R_OK)
except:
  logger.error( "Unable to find/access Open Practice Library %s", oplDir)
  exit(1)
if status:
  logger.info( "Confirmed READ access to Open Practice Library %s", oplDir)
else:
  logger.error( "Do NOT have READ access to Open Practice Library %s", oplDir)
  exit(1)
