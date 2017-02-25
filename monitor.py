import psutil
import time

def monitor():
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
					if '/Users/arunjohnkuruvilla/DF/PROJECT/test.txt' in files.path:
						return True
					
					#print match

			except :
				pass
	return False

while True:
	if monitor():
		print "File being accessed" + time.ctime()