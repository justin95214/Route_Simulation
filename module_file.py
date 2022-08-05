import subprocess
import sys
import warnings
warnings.filterwarnings('ignore')

#package install step


try:	
	import module_source as ms
excpet:
	libraries = ['numpy','pandas', 'io']

	for i in libraries:
		subprocess.check_call([sys.executables, '-m', 'pip', 'install', i])


	import module_source as ms


