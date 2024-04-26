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

- 0 - 7KB blank reserved
- 8KB - 1MB - 4MB U-boot
- 4MB - rest of image/sd/mmc card Linux and your distribution (e.g. Ubuntu / Debian etc)

The idea here is to simply replace the U-boot image in current Linux distribution images. That is about the only way this 'hack'
works.

## References
- [Armbian](https://www.armbian.com/)
- [Orange Pi Zero 3 board](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3.html)
- [Linux Sunxi](https://linux-sunxi.org/Main_Page)
- [U-boot documentation](https://docs.u-boot.org/en/latest/)
