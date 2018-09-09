import os
import sys
import time
from shutil import copyfile
print("Note: if you aren't using venv to run this, you may need to run with admin/root to install python dependencies")
choice = input("Do you have Git installed on your system? (y/N)")

if choice.lower() == "y":
	print("Cloning splatnet2statink")
	print("Source code avaliable at https://github.com/frozenpandaman/splatnet2statink")
	os.system('git clone https://github.com/frozenpandaman/splatnet2statink.git')
	os.system('{} -m pip install -r splatnet2statink/requirements.txt'.format(sys.executable))
	os.system('{} -m pip install -r requirements.txt'.format(sys.executable))
	print("Copying files into right places")
	copyfile("splatnet2statink/dbs.py", "dbs.py")
	copyfile("splatnet2statink/iksm.py", "iksm.py")
	copyfile("splatnet2statink/splatnet2statink.py", "splatnet2statink.py")
	print("Installed!")
	
else:
	print("Please install Git then come back here.")
	time.sleep(3)

