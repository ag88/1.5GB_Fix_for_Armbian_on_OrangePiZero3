# 1.5GB Fix for Armbian on OrangePiZero3

This project attempts a fix or more correctly a hack or workaround to run Armbian on Orange Pi Zero 3 1.5 GB boards.

This project/repository can be classified as a 'hack' or workaround for the '1.5GB issue on Orange Pi 
Zero 3'. It is by no means a 'best' nor appropriate solution. The ideal solution is that the 1.5GB issue can be resolved 
in mainline codes say be correctly detecting 1.5GB memory and that would make this 'hack', workaround, fix unnecessary.
Hence, this should be considered only a 'stop gap' till 'something better' comes about and that solution would likely
supercede this and make this fix redundant.

## Prologue

TLDR,. If you want to use Armbian with Orange Pi Zero 3, get 1GB, 2GB or 4GB boards, and you probably won't need this or any hacks.

### Background

Currently, as of Apr 24, various volunteers in the Armbian community has worked Armbian on
[Orange Pi Zero 3](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3.html) board
and managed to make a port of Armbian (Debian or Ubuntu) Linux distributions run on Orange Pi Zero 3.
A relevant page with links to the images is here

https://www.armbian.com/orange-pi-zero-3/

A relevant discussion thread about the board in Armbian forum is here

https://forum.armbian.com/topic/29202-orange-pi-zero-3/

The port/image is mostly based on Linux 6.6 kernels (and u-boot) and up and has various mainline support for Orange Pi Zero 3
(and Zero 2W) which is based on AllWinner H618 soc/cpu/processor. The current kernels, distributions is able to boot and
work normally on Orange Pi Zero 3 boards with 1 GB / 2 GB / 4 GB dram, but 'crashes' on 1.5 GB boards.

As it turns out as documentation for the dram controller in Allwinner H616/H618 processors is not publicly released, there is no
means to access registers in the dram chips to determine the dram size. Hence, the current memory detection algorithm is also 
pretty much a 'hack' by writing data to memory and reading them back. That seemed like a good strategy to probe for memory size,
but that according to an author who has worked the dram codes:
https://forum.openwrt.org/t/can-someone-make-a-build-for-orange-pi-zero-3/168930/38?u=ag1233
for 1.5GB DDR3 DRAM, the probing algorithm works, but that for DDR4 (it is not known if it is just that particular chip sku) for
1.5GB DDR4 DRAM, apparently address wrap arounds to unknown locations and the probing (writing and reading) back possibly falsely
return correct data. This is trouble and as technically there would be few or no means to generally detect the amount of dram installed.

In the current context, without any fixes, a 1.5GB board is mostly detected as a 2GB board and it 'crashes' on boot.

### An attempt at a fix / hack / workaround

Das U-boot (https://docs.u-boot.org/en/latest/) the booloader for Linux on many embedded Linux SOC / boards boots linux on (most/all?)
linux-sunxi boards. In addition to booting linux, it plays an adjacent often unsung role as 'BIOS' on these boards. One of the 'black
magic' in its functions (this isn't the only 'black magic') is that it initialize, setup and configure DRAM (setup clocks, map addresses?, 
determine dram size) and relocate its own modules into DRAM to run. parse boot scripts, loads linux and subsequently boots the Linux kernel
passing over various required stuff like the device tree, ramdisk etc.

The attempt of this hack / workaround / fix is to make a custom u-boot that would declare the detected dram size as 1.5GB (*hardcoded*).
This obviously is a *bad* solution as practically it only make sense to use this 'hacked' u-boot with 1.5GB boards and only if there are
*no better solutions*. So this fix won't last long as I'd guess sonner than later someone may find a better solution, e.g. to deteect all that
dram correctly.

### simplified layout of Linux distribution image for Orange Pi Zero 3

The (sd card) image for linux distributions for linux-sunxi (or practically on Allwinner SOCs) mostly mostly stick with this format

- 0 - 7KB blank reserved (actually there is something at 0, MBR master boot record and partition table)
- 8KB - 1MB - 4MB U-boot
- 4MB - rest of image/sd/mmc card Linux and your distribution (e.g. Ubuntu / Debian etc)

The idea here is to simply replace the U-boot image in current Linux distribution images. That is about the only way this 'hack'
works.

### the hack

The essence of this fix / hack / workaround is in
```
file: u-boot/arch/arm/mach-sunxi/dram_sun50i_h616.c
static unsigned long mctl_calc_size(const struct dram_config *config)
{       
        u8 width = config->bus_full_width ? 4 : 2;
        
        /* 8 banks */ 
        unsigned long long memsz = (1ULL << (config->cols + config->rows + 3)) * width * config->ranks;    
        log_info("detected memsize %d M\n", (int)(memsz >> 20));
        /* 1.5 GB hardcoded */
        memsz = 2048UL * 1024UL * 1024UL * 3 / 4;
        return memsz;
}
```
take note that the 1.5 GB memory size declaration is *hardcoded*, that practically makes
this fix, hack, workaround only relevant / useful for 1.5 GB boards.

## How to use

To use this modified u-boot, the best practice is to start with / use an image that is known to work on 1GB / 2GB / 4GB Orange Pi Zero 3 boards.
e.g. from https://www.armbian.com/orange-pi-zero-3/

The compiled u-boot binary is:
[u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin](u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin)
 
assuming that your image SD card is mounted at /dev/sdX, you can backup your existing u-boot e.g. 

```
sudo dd if=/dev/sdX of=u-boot-backup.bin bs=1024 skip=8 count=1024
```
that should backup the u-boot in your device to u-boot-backup.bin

then to write the modified u-boot into the SD card it is (be sure that you are writing to the correct device ! mistakes here can corrupt your existing hard disks / storage)
```
sudo dd if=u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin of=/dev/sdX bs=1024 seek=8
```

it may be possible to write that to an existing image file (do backup your image file beforehand)
```
dd if=u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin of=file.img bs=1024 seek=8 conv=notrunc
```
 
### U-boot patcher python script

I've created a 'sd image u-boot patcher' uploaded here in the [tools](tools) folder:
```
usage: sdimage-u-boot-patcher.py [-h] [--nobak] [--ignimgsize] [--bkname BKNAME] image uboot_bin

patch u-boot binary into image

positional arguments:
  image            image file
  uboot_bin        u-boot bin file

options:
  -h, --help       show this help message and exit
  --nobak          do not backup u-boot SPL from image
  --ignimgsize     ignore image size check
  --bkname BKNAME  u-boot SPL backup file name
```
 

you need python3 to use that 'sd image u-boot patcher'
https://www.python.org/downloads/release/python-3123/

run it as
```
python3 sdimage-u-boot-patcher.py imagefile.img u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin 
```
 
This python script will first extract and backup the u-boot binary from the image into
**u-boot-SPL-backup.bin** in the current directory. This helps in case something goofs up,
you can try restoring it with
```
python3 sdimage-u-boot-patcher.py --nobak imagefile.img u-boot-SPL-backup.bin
```

it is a console app, which means that for Windows users, it'd need to be run
in a Cmd prompt window.

note: I've not tried running this patcher script in Windows, only tested in Linux.

This may help for 'Windows' users who may not have access to commands like 'dd' which is mainly available in unix, Linux.

This is so that you can patch the image file directly and perhaps use Balena etcher

https://etcher.balena.io/

or Rufus

https://rufus.ie/en/

to write the image to an SD card / usb drive.
 

In linux, it is found that the sdimage-u-boot-patcher script can actually update /dev/sdX directly. But that it it cannot determine the image size as it is a device and normally it'd need to be run as root.

Hence, I've added a  --ignimgsize  ignore image size check flag for those who wanted to use it that way. e.g.
```
sudo python3 sdimage-u-boot-patcher.py --ignimgsize /dev/sdX u-boot-sunxi-with-spl-2024.04-FixOPiZero3_1.5G.bin 
```

This python script will first extract and backup the u-boot bin image from the image into
**u-boot-SPL-backup.bin** in the current directory. This helps in case something goofs up,
you can try restoring it with
```
sudo python3 sdimage-u-boot-patcher.py --ignimgsize --nobak /dev/sdX u-boot-SPL-backup.bin
```

this is 'slightly safer' than using dd as sdimage-u-boot-patcher actually validates the image format (it look for signatures for a master boot record this can still be confused with a regular disk, and a signature for u-boot at around 8k. it would prompt that the image does not appear to be valid linux image if it either can't find the master boot record 1st sector and the u-boot signature at 8k. you can then stop the patch by pressing control-c or answering 'n' when prompted to continue. for a valid image, it also verifies that the u-boot bin file should not overwrite into the root partition

## Goofy boot u-boot shell

This u-boot image is compiled from the mainline [u-boot sources](https://source.denx.de/u-boot/u-boot)
at release 2024.04. It requires that your distribution image uses /boot/boot.scr or /boot/boot.cmd
in the root filesystem to boot Linux. /boot/boot.scr or /boot/boot.cmd are actually scripts that
contains the u-boot commands to load and boot the Linux kernel along with various dependent
stuff e.g. device tree and ramdisk.

Some distributions has an invalid /boot/boot.scr or /boot/boot.cmd and some other has *customized u-boot* that uses a *customized* boot.scr or boot.cmd file. In those cases you may be dropped into the *u-boot command shell* ! you can try typing '*help*'

that can be quite intimidating to work in the u-boot shell with all that rather complex options.
one way to revert is to restore your backup as covered prior.

for those who would want to venture further google / bing is your friend to search for some aid:
some links I googled:

https://docs.u-boot.org/en/latest/usage/index.html

This is practically the commands to start linux, but that there could be 'surprises' may not work.
https://linux-sunxi.org/U-Boot#Booting_with_boot.cmd

https://krinkinmu.github.io/2023/08/12/getting-started-with-u-boot.html
etc.

## No warranty

and note this is caveat emptor (let the user beware, *use at your own risk*), there is no assurance if after all it fixes anything or break other things.


## References
- [Armbian](https://www.armbian.com/)
- [Orange Pi Zero 3 board](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3.html)
- [Linux Sunxi](https://linux-sunxi.org/Main_Page)
- [U-boot documentation](https://docs.u-boot.org/en/latest/)
