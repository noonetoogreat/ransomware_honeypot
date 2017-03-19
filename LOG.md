# Worklog

## [03-18-2016]
* Continued researching on how to make a kernel dump. Found livekd.exe. 
* livekd.exe requires admin preveleges. Found a method to elevate privileges of the python script.
* livekd.exe requires kd.exe to work. 
* Found Memoryze from FireEye to make a memory dump. But dump not readable by volatility.
* Filedump successfully read by Volatility

## [03-19-2016]
* Integrating memory dumping into monitor.py
