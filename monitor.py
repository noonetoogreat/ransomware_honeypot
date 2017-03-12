import psutil
import time
import sys
import os
import subprocess

safe_pids = []
def monitor(file):
	
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
					if file in files.path:
						'''
						if pinfo['pid'] in safe_pids:
							return False, 0
						else:
							safe_pids.append(pinfo['pid'])
							return True, pinfo['pid']
						'''
						sys.stdout.write('\a')
						print "File being accessed at" + time.ctime() + " by process " + str(pinfo['pid'])
						'''
						proci.suspend()
						
						offpid = pinfo['pid']

						randdump = str(time.time()) + str(offpid) + ".dmp" ;
				
						dumpcmd = os.path.dirname(sys.executable) + "\\" + 'procdump.exe -ma ' + "\"" + str(offpid) + "\"" + ' -accepteula ' + randdump
					
						cmdblock =subprocess.Popen(dumpcmd, stdout=subprocess.PIPE)
						cmdblock.wait()
						
						p.kill()	
						'''
						return True
					
					#print match

			except:
				pass

	return False

def main():
	while True:
		file_to_check = sys.argv[1]
		status = monitor(file_to_check)
		if status == True:
			break	

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print e
		print 'Exiting Monitor.'