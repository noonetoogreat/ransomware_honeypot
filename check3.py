from __future__ import unicode_literals

import os
import time
import datetime
import Queue
import logging

from rattail.win32.service import Service
from rattail.threads import Thread
from rattail.filemon.config import load_profiles
from rattail.filemon.actions import perform_actions
from rattail.filemon.util import queue_existing


# TODO: Would be nice to have a note explaining why this hack exists.
name = __name__
if name == u'win32':
   name = u'rattail.filemon.win32'
log = logging.getLogger(name)


class RattailFileMonitor(Service):
	"""
	Windows service implementation of the File Monitor.
	"""

	_svc_name_ = u"RattailFileMonitor"
	_svc_display_name_ = u"Rattail : File Monitoring Service"
	_svc_description_ = (u"Monitors one or more folders for incoming files, "
						 u"and performs configured actions as new files arrive.")

	def __init__(self, config):
		print config

		"""
		Service initialization.
		"""
		# Read monitor profile(s) from config.
		self.monitored = load_profiles(config)

		# Make sure we have something to do.
		if not self.monitored:
			return False

		# Create monitor and action threads for each profile.
		for key, profile in self.monitored.iteritems():

			# Create a file queue for the profile.
			profile.queue = Queue.Queue()

			# Perform setup for each of the watched folders.
			for i, path in enumerate(profile.dirs, 1):

				# Maybe put all pre-existing files in the queue.
				if profile.process_existing:
					queue_existing(profile, path)

				# Create a watcher thread for the folder.
				name = u'watcher_{0}-{1}'.format(key, i)
				log.debug(u"starting {0} thread for folder: {1}".format(repr(name), repr(path)))
				thread = Thread(target=watch_directory, name=name, args=(profile, path))
				thread.daemon = True
				thread.start()

			# Since `ReadDirectoryChangesW()` doesn't guarantee we'll receive
			# all file events, maybe make a "fallback" watcher thread as well.
			if profile.fallback_watcher_enable:
			   name = 'fallback-watcher-{0}'.format(key)
			   log.debug("starting fallback watcher thread: {0}".format(name))
			   thread = Thread(target=fallback_watcher, name=name, args=(profile,))
			   thread.daemon = True
			   thread.start()

			# Create an action thread for the profile.
			name = u'actions_{0}'.format(key)
			log.debug(u"starting action thread: {0}".format(repr(name)))
			thread = Thread(target=perform_actions, name=name, args=(profile,))
			thread.daemon = True
			thread.start()

		return True
	

def watch_directory(profile, path):
	"""
	Callable target for watcher threads.
	"""

	import win32file
	import win32con
	import winnt

	hDir = win32file.CreateFile(
		path,
		winnt.FILE_LIST_DIRECTORY,
		win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
		None,
		win32con.OPEN_EXISTING,
		win32con.FILE_FLAG_BACKUP_SEMANTICS,
		None)

	if hDir == win32file.INVALID_HANDLE_VALUE:
		log.error(u"can't open directory with CreateFile(): {0}".format(repr(path)))
		return

	while True:
		results = win32file.ReadDirectoryChangesW(
			hDir,
			1024,
			False,
			win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

		log.debug(u"ReadDirectoryChangesW() returned: {0}".format(repr(results)))
		for action, fname in results:
			fpath = os.path.join(path, fname)
			queue = False
			if profile.watch_locks:
				if action == winnt.FILE_ACTION_REMOVED and fpath.endswith('.lock'):
					fpath = fpath[:-5]
					queue = True
			else:
				if action in (winnt.FILE_ACTION_ADDED, winnt.FILE_ACTION_RENAMED_NEW_NAME):
					queue = True
			if queue:
				log.debug(u"queueing {0} file: {1}".format(repr(profile.key), repr(fpath)))
				profile.queue.put(fpath)


def fallback_watcher(profile):
	"""
	Fallback watcher thread, to deal with any files which the primary watchers
	may have missed.  While it doesn't often happen, sometimes the Windows API
	`ReadDirectoryChangesW()`_ function can "miss" file events.  The primary
	watchers rely on that exclusively, so this function provides a workaround
	to the problem.  See also this `Stack Overflow post`_.

	.. _`ReadDirectoryChangesW()`: https://msdn.microsoft.com/en-us/library/windows/desktop/aa365465%28v=vs.85%29.aspx
	.. _`Stack Overflow post`: http://stackoverflow.com/questions/57254/how-to-keep-readdirectorychangesw-from-missing-file-changes
	"""
	started = datetime.datetime.now()
	max_delta = datetime.timedelta(seconds=profile.fallback_watcher_maxage)
	min_delta = datetime.timedelta(seconds=profile.fallback_watcher_minage)

	while True:

	   # Wait the configured number of seconds before looking for files.
	   time.sleep(profile.fallback_watcher_delay)

	   # Find the timestamp range we're interested in, each time we look.
	   now = datetime.datetime.now()
	   min_time = now - max_delta
	   if min_time < started:
		  min_time = started
	   max_time = now - min_delta

	   # Inspect all files within all watched folders.
	   for path in profile.dirs:
		  for fn in os.listdir(path):
			 fpath = os.path.join(path, fn)

			 # We only want files; no folders etc.  Note that if the primary
			 # watcher noticed and is handling this file, it very well could
			 # have disappeared already.
			 try:
				if not os.path.isfile(fpath):
				   continue
				modtime = os.path.getmtime(fpath)
			 except WindowsError:
				log.debug("file presumably disappeared: {0}".format(fpath))
				continue

			 # Queue file for processing only if its last modification time
			 # falls within our calculated range.  We filter thus in order to
			 # avoid files which may be old enough to have already been queued
			 # at service start via the `process_existing` setting, and to
			 # avoid files which may be new enough to have been queued by the
			 # primary watcher threads.
			 modtime = datetime.datetime.fromtimestamp(modtime)
			 if min_time <= modtime <= max_time:

				# Ignore lock files, but only if the profile is configured to
				# watch for them in general.  If lock files are *supposed* to be
				# involved, and one is still hanging around at this point, that
				# presumably points to a different problem than the one we're
				# trying to solve here...
				if profile.watch_locks and fpath.endswith('.lock'):
				   continue

				log.warning("queueing {0} file: {1}".format(repr(profile.key), repr(fpath)))
				profile.queue.put(fpath)

			 else:
				log.debug("ignoring file due to age ({0} seconds): {1}".format(
				   (now - modtime).seconds, fpath))


if __name__ == '__main__':
	import win32serviceutil
	win32serviceutil.HandleCommandLine(RattailFileMonitor)