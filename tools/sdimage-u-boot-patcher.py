#!/usr/bin/env python3
#usage: sdimage-u-boot-patcher.py [-h] [--nobak] [--ignimgsize] [--bkname BKNAME] image uboot_bin
#
#patch u-boot binary into image
#
#positional arguments:
#  image            image file
#  uboot_bin        u-boot bin file
#
#options:
#  -h, --help       show this help message and exit
#  --nobak          do not backup u-boot SPL from image
#  --ignimgsize     ignore image size check
#  --bkname BKNAME  u-boot SPL backup file name
#
import sys
import os
import argparse
import struct
import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description='patch u-boot binary into image')
parser.add_argument("--nobak", help="do not backup u-boot SPL from image", required=False, action='store_true')
parser.add_argument("--ignimgsize", help="ignore image size check", required=False,\
    action='store_true')
parser.add_argument("--bkname", help="u-boot SPL backup file name", required=False,\
    default="u-boot-SPL-backup.bin", action='store')
parser.add_argument("image", help="image file", nargs=1, action='store')
parser.add_argument("uboot_bin", help="u-boot bin file", nargs=1, action='store')

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(0)

cmdargs = parser.parse_args(sys.argv[1:])

if not Path(cmdargs.image[0]).exists():
    print("image file {} not found".format(cmdargs.image[0]))
    sys.exit(1)

if not Path(cmdargs.uboot_bin[0]).exists():
    print("uboot bin file {} not found".format(cmdargs.uboot_bin[0]))
    sys.exit(1)

sz_image = os.stat(cmdargs.image[0]).st_size
sz_uboot = os.stat(cmdargs.uboot_bin[0]).st_size
print("image {} size:{}".format(cmdargs.image[0],sz_image))
print("uboot bin {} size:{}".format(cmdargs.uboot_bin[0],sz_uboot))

if not cmdargs.ignimgsize and sz_image == 0:
    print("image file {} is empty".format(cmdargs.image[0]))
    sys.exit(1)

if sz_uboot == 0:
    print("uboot bin file {} is empty".format(cmdargs.uboot_bin[0]))
    sys.exit(1)

if not cmdargs.ignimgsize and sz_image < sz_uboot:
    print("image file {} is invalid, it is smaller than u-boot file {}"\
        .format(cmdargs.image[0],cmdargs.uboot_bin[0]))
    sys.exit(1)

#validate image file
validimage = False
with open(cmdargs.image[0], mode='rb') as imf:
    #default uboot_szlimit in k bytes
    uboot_szlimit = 1024
    try: 
        # checks for master boot record
        imf.seek(0x1fe)
        bootsig = imf.read(2)
        if not bootsig == bytes.fromhex('55 aa'):
            raise Exception('invalid mbr sig')
        # checks for u-boot sig
        imf.seek(0x2004)
        ubootsig = imf.read(4)
        #print(ubootsig.decode('utf-8'))
        if not ubootsig.decode('utf-8') == "eGON":
            raise Exception('invalid uboot sig')
        # partition 0
        imf.seek(0x1be)
        buf = imf.read(16)
        partentry = dict()
        pe = struct.unpack('<BBHBBHLL',buf)
        partentry['boot'] = pe[0]
        partentry['shead'] = pe[1]
        partentry['ssect'] = pe[2] & 0x3f
        partentry['scyl'] = (pe[2] >> 8) | (((pe[2] & 0xff )>>6) << 8)
        partentry['ID'] = pe[3]
        partentry['ehead'] = pe[4]
        partentry['esect'] = pe[5] & 0x3f
        partentry['ecyl'] = (pe[5] >> 8) | (((pe[5] & 0xff )>>6) << 8)
        partentry['lba_start'] = pe[6]
        partentry['lba_count'] = pe[7]
        print("image file {} partition info".format(cmdargs.image[0]))
        print(partentry)
        # linux partition
        if not partentry['ID'] == 0x83:
            raise Exception('invalid part entry')
        if partentry['lba_start'] > 0:
            uboot_szlimit = int(( partentry['lba_start'] - 1 ) * 512 / 1024 ) - 8
        else:
            lba = (partentry['scyl']*16 + partentry['shead'])*63 + (partentry['ssect'] - 1)
            uboot_szlimit = int(( lba - 1 ) * 512 / 1024 ) - 8
        validimage = True
    except Exception as e:
        msg = "The image file {} does not appear ".format(cmdargs.image[0]) + \
          "to be a valid linux filesystem image, continue? (y/n)"
        ans = input(msg)
        if not ans is None and ans[0].lower() == 'y':
            uboot_szlimit = 1024
            validimage = False
        else:
            sys.exit(2)

#print(validimage)

with open(cmdargs.uboot_bin[0], mode='rb') as ubf:
    try:
        # checks for u-boot sig
        ubf.seek(0x04)
        ubootsig = ubf.read(4)
        #print(ubootsig.decode('utf-8'))
        if not ubootsig.decode('utf-8') == "eGON":
            raise Exception('invalid uboot sig')
    except Exception as e:
        msg = "The uboot bin file {} does not appear ".format(cmdargs.uboot_bin[0]) + \
          "to be valid, continue? (y/n)"
        ans = input(msg)
        if not ans is None and not ans[0].lower() == 'y':
            sys.exit(2)

if sz_uboot > uboot_szlimit*1024:
    if validimage:
        print("error uboot bin file {} size {} will overwrite filesystem, not patching".\
            format(cmdargs.uboot_bin[0], sz_uboot))
        sys.exit(1)
    else:
        msg = "warning uboot bin file {} size {} exceeds {} Kbytes, continue (y/n)".\
            format(cmdargs.uboot_bin[0], sz_uboot, uboot_szlimit)
        ans = input(msg)
        if ans is not None and not ans[0].lower() == 'y':
            sys.exit(1)

#backup the u-boot from the image
if not validimage and not cmdargs.nobak :
    print("unable to determine if image {} is valid, unable to backup u-boot from image not patchinng".\
        format(cmdargs.image[0]))
    sys.exit(1)
elif not cmdargs.nobak and validimage:
    imname = cmdargs.image[0]
    bkname = cmdargs.bkname
    if Path(bkname).exists():
        print("u-boot backup file {} exists, please rename or remove".format(bkname))
        sys.exit(1)
    with open(imname, mode='rb') as imf:
        buffer = None
        count = (uboot_szlimit-1)*1024
        try:
            # slurp the whole u-boot image backup into buffer 
            imf.seek(8192)
            buffer = imf.read(count)
        except IOError as e:
            print("Unable read data from image file {}".format(imname))
            print(e)
            sys.exit(1)
        except Exception as e:
            print("Unable read data from uboot bin file {}".format(imname))
            print('error: ' + e, sys.exc_info())
            sys.exit(1)
        if not buffer == None:
            try:
                with open(bkname, mode='wb') as ubf:
                    ubf.write(buffer)
                    ubf.flush()
                print("uboot from image file {} backup into {} file"\
                    .format(imname, bkname))
            except IOError as e:
                print("Unable write data to backup file {}".format(bkname))
                print(e)
                sys.exit(1)
            except Exception as e:
                print("Unable write data to backup file {}".format(bkname))
                print('error: ' + e, sys.exc_info())
                sys.exit(1)

#patch u-boot into image file
with open(cmdargs.image[0], mode='rb+') as imf:
    buffer = None
    with open(cmdargs.uboot_bin[0], mode='rb') as ubf:
        try:
            # slurp the whole u-boot bin into buffer :p
            buffer = ubf.read(sz_uboot)
        except IOError as e:
            print("Unable read data from uboot bin file {}".format(cmdargs.uboot_bin[0]))
            print(e)
            sys.exit(1)
        except Exception as e:
            print("Unable read data from uboot bin file {}".format(cmdargs.uboot_bin[0]))
            print('error: ' + e, sys.exc_info())
            sys.exit(1)
    if not buffer == None:
        try:
            imf.seek(8192)
            imf.write(buffer)
            imf.flush()
            print("uboot bin file {} patched into image file {}"\
                .format(cmdargs.uboot_bin[0],cmdargs.image[0]))
        except IOError as e:
            print("Unable write data to image file {}".format(cmdargs.image[0]))
            print(e)
            sys.exit(1)
        except Exception as e:
            print("Unable write data to image file {}".format(cmdargs.image[0]))
            print('error: ' + e, sys.exc_info())
            sys.exit(1)

