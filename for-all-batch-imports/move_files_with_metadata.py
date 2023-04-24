import pandas as pd #used for loading in spreadsheets
#for interacting with the system:
import os
import glob
import sys
from shutil import copy2 as copyfile
#numerical python, I only use to make sure some fields are numbers
import numpy as np

def main():
    #load metadata template
    with open('metadata_template_dublin_core_2.xml', 'r+') as f:
        metadata = f.readlines() #load it line by line for later
    #load spreadsheet as a pandas dataframe
    df = pd.read_excel('masterspreadsheet_edited.xlsx') #uncomment the appropriate one
    # df = pd.read_csv('masterspreadsheet_openrefine.csv') #uncomment the appropriate one
     
    for i, row in df.iterrows(): #go through rows in spreadsheet
        if i%100==0: #to keep track of progress
            print("%i / %i"%(i, len(df)))
        #skip rows with no associated image
        if ('ERROR' in row['Image file']) or ('Could not' in row['Image file']): 
            continue
        #skip rows from Aberdeen
        if ('Aberdeen City' in row['Present-day Location Authority']) or ('Aberdeen City' in row['Original Location Authority']):
            continue
        #get location of images and folder
        impath = row['Image file'].replace('D:\Towerblock Digitised Images', '.')
        imfold = os.path.split(impath)[0]
        
        #name of development
        development = row['Original Development name(s)']
            
        #other info about development
        #city
        if type(row['Present-day Location Authority']) == str:
            city = make_city(row['Present-day Location Authority'])
        else:
            city = make_city(row['Original Location Authority'])
       
       #year photo was taken (if present)
        if 'Error' in str(row['Image date']):
            year_taken = 'unknown'
        else:
            year_taken = str(int(row['Image date']))
        description = make_description(row)
        
        #write metadata
        metadata_temp = ''
        for line in metadata:
            #skip lines as necessary
            if year_taken=='unknown' and 'substitute-me-year' in line:
                continue
            elif 'country' in line:
                continue
            
            #add info to metadata template if substitution necessary
            # if dataset title line (three substitutions on this line)
            if 'substitute-me-city' in line:
                if 'substitute-me-development' in line:
                    metadata_temp = metadata_temp + line.replace('substitute-me-city', city).replace('substitute-me-development', development)
                else:
                    metadata_temp = metadata_temp + line.replace('substitute-me-city', city)
                if 'substitute-me-image' in line: 
                    metadata_temp = metadata_temp + line.replace('substitute-me-image', row['Image name'])
            
            elif 'substitute-me-abstract' in line:
                metadata_temp = metadata_temp + line.replace('substitute-me-abstract', description)
            elif 'substitute-me-year' in line:
                metadata_temp = metadata_temp + line.replace('substitute-me-year', year_taken)
            else: #if no substitution necessary, just copy line (e.g. for keywords)
                metadata_temp = metadata_temp + line
        
        outfold = 'processed/%s-%s-%s'%(city, development, row['Image name']) #folder to write output to
        outfold = outfold.replace(':', '_')
        os.makedirs(outfold, exist_ok=True)
        with open(outfold +'\\dublin_core.xml', 'w+') as f:
            f.write(metadata_temp)
        
        #add placeholder for testing (comment out when using for real)
        # with open(outfold + '\\placeholder.txt', 'w+') as f:
            # f.write(impath)
        
        #copy image file (uncomment when using for real)
        copyfile(impath, outfold)
        
    sys.exit(0)

def make_city(council):
    #get the city by removing generic words from council names
    exclusion = ['Borough', 'Metropolitan', 'Council', 'Urban', 'District', 'Burgh', 'Development', 'Corporation']
    council_out = council
    for word in exclusion:
        council_out = council_out.replace(word, '')
    council_out = council_out.strip() #remove spaces at start/end of city
    return(council_out)

def make_description(row):
    #get information from the spreadsheet row and put it into a human-readable description
    if np.isfinite(row['Construction completion date']) and np.isfinite(row['Construction start date']): #if there's an end date
        construction_year = "%i-%i"%(row['Construction start date'], row['Construction completion date'])
    elif np.isfinite(row['Construction start date']): #if there's a start date
        construction_year = str(int(row['Construction start date']))
    elif np.isfinite(row['Construction completion date']): #if there's an end date
        construction_year = str(int(row['Construction completion date']))
    else:#otherwise, skip construction years in description
        return(f"Multi-storey block details: {row['Multi-storey block details']}; Multi-storey block name(s): {row['Multi-storey block name(s)']}; Image detail: {row['Image details']} Original Commissioning Authority: {row['Original Commissioning Authority']}; Image taken: {row['Image date']};Context: Tower Block UK is a project supported by the Heritage Lottery Fund, bringing together public engagement and an openly-licensed image archive in an attempt to emphasise the social and architectural importance of tower blocks, and to frame multi-storey social housing as a coherent and accessible nationwide heritage. The Tower Block UK image archive is a searchable database of around 4,000 images of every multi-storey social housing development built in the UK. The photographs were largely taken in the 1980s by Miles Glendinning and are made available here for public use. As many of the blocks documented and photographed have since been demolished, the archive functions in part as a repository of information on an important aspect of UK heritage that is now vanishing. The archive itself catalogues multi-storey blocks as part of the developments within which they were initially commissioned and built. It gives details of notable dates, such as when local authorities approved the developments and when construction began or finished. Alongside this, the archive provides information on the local authorities, architects, and other agents involved in the processes of commissioning, designing, and constructing mass social housing. While the most historically 'accurate' identification labels in the database are the original overall development or project names, the archive also contains details of the individual blocks built.")
    if 'Error' in str(row['Image date']):
        row['Image date'] = 'unknown'
    description = f"Multi-storey block details: {row['Multi-storey block details']}; Multi-storey block name(s): {row['Multi-storey block name(s)']}; Image detail: {row['Image details']} Original Commissioning Authority: {row['Original Commissioning Authority']}; Construction period (from/to): {construction_year}; Image taken: {row['Image date']}; Context: Tower Block UK is a project supported by the Heritage Lottery Fund, bringing together public engagement and an openly-licensed image archive in an attempt to emphasise the social and architectural importance of tower blocks, and to frame multi-storey social housing as a coherent and accessible nationwide heritage. The Tower Block UK image archive is a searchable database of around 4,000 images of every multi-storey social housing development built in the UK. The photographs were largely taken in the 1980s by Miles Glendinning and are made available here for public use. As many of the blocks documented and photographed have since been demolished, the archive functions in part as a repository of information on an important aspect of UK heritage that is now vanishing. The archive itself catalogues multi-storey blocks as part of the developments within which they were initially commissioned and built. It gives details of notable dates, such as when local authorities approved the developments and when construction began or finished. Alongside this, the archive provides information on the local authorities, architects, and other agents involved in the processes of commissioning, designing, and constructing mass social housing. While the most historically 'accurate' identification labels in the database are the original overall development or project names, the archive also contains details of the individual blocks built."
    return(description)

if __name__ == '__main__':
    main()
    
