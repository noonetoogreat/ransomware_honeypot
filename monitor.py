import psutil
import time
import sys

safe_pids = []
def monitor():
	'''
	file_to_check = sys.argv[1]
	global safe_pids
	for proc in psutil.process_iter():
		try:
			pinfo = proc.as_dict(attrs=['pid'])
		except psutil.NoSuchProcess:
			pass
		else:
			try:
				proci = psutil.Process(pinfo['pid'])
				for files in proci.open_files() :
					#print files.path
					#handles = re.match(my_regex, files, re.IGNORECASE)
					if file_to_check in files.path:
						
						if pinfo['pid'] in safe_pids:
							return False, 0
						else:
							safe_pids.append(pinfo['pid'])
							return True, pinfo['pid']
						
						return True, pinfo['pid']
					
					#print match

			except :
				pass
	return False, 0
	'''

def main():
	'''
	while True:
		status, pid = monitor()
		if status:
			sys.stdout.write('\a')
			print "File being accessed at" + time.ctime() + " by process " + str(pid)
	'''
	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    observer.join()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print e
		print 'Exiting Monitor.'