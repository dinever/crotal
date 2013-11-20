#!/usr/bin/python

import os

def copyDir(srcDir, tarDir):
    for item in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, item)
        tarFile = os.path.join(tarDir, item)

        if os.path.isfile(srcFile):
            if os.path.exists(tarDir) is False:
                os.makedirs(tarDir)
            if os.path.exists(tarDir) is False or (os.path.exists(tarDir) and (os.path.getsize(srcFile))):
                open(tarFile, "wb").write(open(srcFile, "rb").read())
            else:
                pass

        if os.path.isdir(srcFile):
            copyDir(srcFile, tarFile)

if __name__ == '__main__':
    copyDir(srcDir, tarDir)
