import os

def main():
    for fold in os.listdir('./'): #iterate through folders
        if not os.path.isdir(fold):
            continue
        filelist = os.listdir(fold) #get list of files within folder
        with open("%s/contents"%fold, 'w+') as f:
            for file in filelist:
                #skip metadata and contents
                if 'contents' in file or 'dublin_core.xml' in file:
                    continue
                else:
                    f.write("%s\n"%file)

if __name__=='__main__':
    main()