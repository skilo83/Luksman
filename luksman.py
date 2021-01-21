#!/usr/bin/python3

"""
Copyright (C) 2021  Anonymous
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.
"""

import os
import sys
import string
import secrets
import subprocess

is_root = os.getuid() == 0
 
def createNewContainer(mappingName):
	containerName = input("Enter a name for the container file:\n")
	containerSize = input("Please enter a size in MB for the container: ")
	if (int(containerSize) < 50):
		print("You must enter a size greater than 49MB")
		sys.exit(1)
		
	tuple1 = (containerSize, "M")
	containerSize = "".join(tuple1)
	
	ret = subprocess.call(["truncate", "-s", containerSize, containerName])
	print("LUKS setup..\n")
	
	ret = subprocess.call(["cryptsetup",
	"luksFormat",
	"--cipher=aes-xts-plain64",
	"--key-size=512",
	"--pbkdf=argon2i",
	"--pbkdf-memory=128",
	containerName])
	
	if (int(ret) != 0):
		print("An error occoured.\n")
		sys.exit(1)
		
	print("Enter the password you just created\n")
	ret = subprocess.call(["cryptsetup", "luksOpen", containerName, mappingName])
	
	if (int(ret) != 0):
		print("An error occoured.\n")
		sys.exit(1)
		
	tuple2 = ("/dev/mapper/", mappingName)
	mapPath = "".join(tuple2)
		
	print("Formatting the container file\n")
	
	ret = subprocess.call(["mkfs.ext4", "-O", "^has_journal", "-j", mapPath])
	
	if (int(ret) != 0):
		print("mkfs failed to format the container.\n")
		sys.exit(1)
		
	print("Creating mount point\n")
	randMountPoint = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(0, 24))
	tuple2 = ("/mnt/containers/luks/", randMountPoint)
	mountPoint = "".join(tuple2)
	#mkdir has no return value
	ret = subprocess.call(["mkdir", "-p", mountPoint], stdout=subprocess.DEVNULL)
	
	print("Mounting..\n")
	ret = subprocess.call(["mount", mapPath, mountPoint])
	
	if (int(ret) != 0):
		print("Mount failed. Exiting..")
		sys.exit(1)
	
	print("Done!")
	print("Container mount point: ", mountPoint)
	print("LUKS mapper: ", mapPath)
	input("Press enter to return to main menu")
 
def openContainer(containerFileName):
	randMapName = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(0, 24))
	ret = subprocess.call(["cryptsetup", "luksOpen", containerFileName, randMapName])
	
	if (int(ret) != 0 ):
		print("error opening container.\n")
		sys.exit(1)
		
	tuple2 = ("/dev/mapper/", randMapName)
	mapPath = "".join(tuple2)
	
	print("Creating mount point\n")
	randMountPoint = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(0, 24))
	tuple2 = ("/mnt/containers/luks/", randMountPoint)
	mountPoint = "".join(tuple2)
	#mkdir has no return value
	ret = subprocess.call(["mkdir", "-p", mountPoint], stdout=subprocess.DEVNULL)
	
	print("Mounting..\n")
	ret = subprocess.call(["mount", mapPath, mountPoint])
	
	if (int(ret) != 0):
		print("Mount failed. Exiting..")
		sys.exit(1)
		
	print("Success!", str(containerFileName), "is mounted at ", mountPoint, "\n")
	input("Press enter to return to main menu")
 
def closeContainer(mappingName):
	print("Unmounting container..\n")
	tuple2 = ("/dev/mapper/", mappingName)
	mapPath = "".join(tuple2)
	
	ret = subprocess.call(["umount", mapPath])
	ret = subprocess.call(["cryptsetup", "luksClose", mappingName])
	if (int(ret) != 0):
		print("\nAn error occoured while unmounting ", mapPath)
		input("\nPress enter to return to main menu")
	else:
		input("\nDone! Press enter to return to main menu")
	
	return
 
def containerStatus(mappingName):
	ret = subprocess.call(["cryptsetup", "status", mappingName])
	input("Press enter to return to main menu")
	os.system("clear")
	
def cleanMountPoints():
	#delete all the mount points in /mnt/containers/
	ret = subprocess.call(["rm", "-rf", "/mnt/containers/luks/"])
	print("\n")
	input("Done. Press enter to return to main menu.")
 
def main():
 
	os.system("clear")
	if (not is_root):
		print("Run it as root.")
		sys.exit(0)
	
	while True:
		os.system("clear")
		print("*** LUKS Manager by Anonymous ***\n")
		print("Active mapping names:")
		ret = subprocess.call(["dmsetup", "ls"])
		print("\nWhat would you like to do?")
		print("1 = Create a new LUKS container.")
		print("2 = Open a LUKS container.")
		print("3 = Close a LUKS container.")
		print("4 = Check status of a LUKS mapping name.")
		print("5 = Clean mount points.")
		print("6 = Exit.\n")
		answer = input("> ")
		os.system("clear")
		
		if (str(answer) == "1"):
			randMapName = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(0, 24))
			createNewContainer(randMapName)
		elif (str(answer) == "2"):
			c = input("Container file to open: ")
			openContainer(str(c))
		elif (str(answer) == "3"):
			print("Active mapping names:")
			ret = subprocess.call(["dmsetup", "ls"])
			print("\n")
			c = input("Enter mapping name: ")
			closeContainer(str(c))
		elif (str(answer) == "4"):
			print("Active mapping names:")
			ret = subprocess.call(["dmsetup", "ls"])
			print("\n")
			c = input("Enter mapping name: ")
			containerStatus(str(c))
		elif (str(answer) == "5"):
			print("Active mapping names:")
			ret = subprocess.call(["dmsetup", "ls"])
			print("\nWARNING. Do not proceed if mapping names are active.\n")
			try:
				input("Press enter to proceed or ctrl+c to abort.")
				cleanMountPoints()
			except KeyboardInterrupt:
				print("Aborted.")
		elif (str(answer) == "6"):
			sys.exit(0)
 
if __name__=='__main__':
	main()
