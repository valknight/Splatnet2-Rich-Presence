import os
import sys
import time
from shutil import copyfile, rmtree

blacklist = ["README.md", "requirements.txt", ".gitignore"]
print("Note: if you aren't using venv to run this, you may need to run with admin/root to install python dependencies")
choice = input("Do you have Git installed on your system? (y/N)")

if choice.lower() == "y":
    print("Cloning splatnet2statink")
    rmtree("splatnet2statink", ignore_errors=True)
    print("Source code avaliable at https://github.com/frozenpandaman/splatnet2statink")
    os.system('git clone https://github.com/frozenpandaman/splatnet2statink.git')
    os.system(
        '{} -m pip install -r splatnet2statink/requirements.txt --user'.format(sys.executable))
    os.system('{} -m pip install -r requirements.txt --user'.format(sys.executable))
    print("Copying files into right places")
    to_copy = os.listdir("splatnet2statink")
    print(to_copy)
    for file in to_copy:
        file_current = os.path.join("splatnet2statink", file)
        try:
            if file not in blacklist:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass
                copyfile(file_current, "./{}".format(file))
                print("Copied {}".format(file))
        except IsADirectoryError:
            pass
    print("All files copied, cleaning up...")
    rmtree("splatnet2statink", ignore_errors=True)


else:
    print("Please install Git then come back here.")
    time.sleep(3)
