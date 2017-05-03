# -*-coding:GB18030-*-

"""
Created on 4/28/2017
Copyright (c) Nick Bao. All rights reserved.
it's tested on windows with Python 3.5.2 only
"""
import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import converter
from converter import Converter
video_converter = Converter()


def get_minimum_creation_time(exif_data):
    mtime = "2020:12:30 00:00:00"
    if 306 in exif_data and exif_data[306] < mtime: # 306 = DateTime
        mtime = exif_data[306]
    if 36867 in exif_data and exif_data[36867] < mtime: # 36867 = DateTimeOriginal
        mtime = exif_data[36867]
    if 36868 in exif_data and exif_data[36868] < mtime: # 36868 = DateTimeDigitized
        mtime = exif_data[36868]
    mtime = mtime[0:10].replace(':', '-')
    return mtime

def get_creationdate_with_filename_as_dict(sourc_dir, by_file_name):
    print("Processing all image files in: %s", source_dir)
    result = {}
    counter = 0
    folder = sourc_dir
    print("- " + folder)
    #for f in os.listdir(folder):
    for (dirname, dirshere, fileshere) in os.walk(folder):
        for f in fileshere :
            counter += 1
            #fullFileName = folder + "\\" + f
            fullFileName = os.path.join(dirname, f)
            print('counter = %d,  file is %s' %(counter, fullFileName))
            if f == '.picasa.ini' or f == 'Thumbs.db':
                print("skip .picasa.ini or Thumbs.db")
                continue

            if counter == 50:
                print('stop here')
            if by_file_name:  # wrong exif info
                mtime = os.path.basename(fullFileName)
                mtime = mtime[:6]
                mtime = mtime[:4] + '-' + mtime[4:]
            else:
                mtime = '2020-12-30'
                try:
                    img = Image.open(fullFileName)
                except Exception as e:
                    print(" '%s' as image open failing due to exception: %s"%(f, e))
                    image_open_fail = True
                if image_open_fail:
                    try:
                        video_info = video_converter.probe(fullFileName)
                    except Exception as e:
                        print("   Skipping file %s(can't open as image and video file: %s" %(f, e))
                        video_open_fail = True
                        continue
                    # treat as video file
                    v_stream = video_info.streams #metadata.creation_time
                    min_creation_time = '2020:12:30 00:00:00'
                    for stream in v_stream:
                        v_metadata = stream.metadata

                        v_creation_time = v_metadata.get('creation_time', min_creation_time)
                        v_creation_time = v_creation_time.replace('-', ':')
                        if v_creation_time < min_creation_time:
                            min_creation_time = v_creation_time

                    mtime = min_creation_time[0:10].replace(':', '-')

                else:  #open as image success
                    try:
                        img_exif = img._getexif()
                    except Exception as e:
                        print("    Can't read EXIF from '%s' due to exception: %s"%(f, e))
                        img_exif = None
                    if img_exif:
                        mtime = get_minimum_creation_time(img_exif)

                if  mtime == '2020-12-30':  #wrong exif info or no creation time in video
                    mtime = os.path.basename(fullFileName)
                    mtime = mtime[:6]
                    mtime = mtime[:4] + '-' + mtime[4:]
                    #test the mtime range
                    mtime_year = mtime[:4]
                    mtime_isvalid = False
                    if mtime_year.isdigit() and mtime_year > "2000" and mtime_year < "2018" :
                        #test the month
                        mtime_month = mtime[-2:]
                        if mtime_month.isdigit() and mtime_month > "01" and mtime_month < "12":
                            mtime_isvalid = True
                    if not mtime_isvalid:
                        mtime1 = os.path.getctime(fullFileName)
                        mtime2 = os.path.getmtime(fullFileName)
                        idate = mtime1 if mtime1 < mtime2 else mtime2
                        idate = datetime.datetime.fromtimestamp(idate)
                        mtime = idate.date().isoformat()



            i = 0
            while mtime+"_"*i in result:
                i += 1
            mtime = mtime+"_"*i
            result[mtime] = fullFileName
    for key in sorted(result):
        print(key, result[key])
    print("  Found %s orignal files in %s."%(counter, folder))
    print("Added total of %s to dictionary."%len(result))
    return result
def copy_from_image_dict_to_directory(image_dict, output_dir, move_file):
    assert os.path.exists(output_dir)
    for i,key in enumerate(sorted(image_dict)):
        source_file_name_base, extension =  os.path.splitext(image_dict[key])
        source_file_name_base = os.path.basename(source_file_name_base)
        new_file_name = source_file_name_base + extension
        dir_name = key[:7]
        full_dir_name = os.path.join(output_dir, dir_name)
        if not os.path.exists(full_dir_name):
            os.makedirs(full_dir_name)
        output_file = os.path.join(full_dir_name, new_file_name)
        append = 1
        while os.path.exists(output_file):
            new_file_name = source_file_name_base + '_' + str(append) + extension
            append += 1
            output_file = os.path.join(full_dir_name, new_file_name)
        if move_file:
            shutil.move(image_dict[key], output_file)
        else:
            shutil.copy2(image_dict[key], output_file)
    print("Copied %s files to %s"%(i+1, output_dir))
if __name__=="__main__":
    #source_dir = r"D:\final_photo\03_瑶瑶家生活\temp-new-doublekiller-pass"
    #output_dir = r"D:\final_photo\03_瑶瑶家生活"
    source_dir = r"/media/nick/Jade250G/final_photo/03_瑶瑶家生活/temp-new-doublekiller-pass"
    output_dir = r"/media/nick/Jade250G/final_photo/03_瑶瑶家生活"

    # obtain /var/tmp/images/iPhone, /var/tmp/images/CanonPowerShot, /var/tmp/images/Nikon1
    all_files = get_creationdate_with_filename_as_dict(source_dir, by_file_name=False)
    copy_from_image_dict_to_directory(all_files, output_dir,move_file=True)