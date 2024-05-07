# Build guide

## prequisites

- This is based on Ubuntu Jammy 22.04

- gcc-aarch64-linux and cpp-11-aarch64-linux-gnu cross compiler

```
apt install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu gcc-11-aarch64-linux-gnu-base gcc-11-aarch64-linux-gnu cpp-aarch64-linux-gnu cpp-11-aarch64-linux-gnu
```

- gnu quilt (optional)
```
apt install quilt
```
if you do not install quilt, you can apply the patches in [patches](patches) directory manually using `patch` command, the sequence is given in [patches/series](patches/series).

## steps

1 update submodules if necessary 

  if you have done:
  ```
  git clone --recurse-submodules https://github.com/ag88/1.5GB_Fix_for_Armbian_on_OrangePiZero3.git
  ```
  you the sub-modules should have been setup, otherwise
  ```
  git submodule init
  git submodule update
  ```

1a optional: checkout u-boot branch v2024.04
  ```
  cd u-boot
  git tag  <- you should see the tag v2024.04
  git checkout v2024.04
  ```
  otherwise, normally it is the head/main branch. Try this step if you get patch errors or
  errors during compile

2 apply the patches
  ```
  quilt push -a
  ```

3 compile arm-trusted-firmware
  ```
  cd arm-trusted-firmware
  bash arm-trust-fw-make.sh
  ```

4 compile u-boot
  ```
  cd u-boot
  bash build.sh
  ```
  If the build goes well you should find **u-boot-sunxi-with-spl.bin** in u-boot folder.
  That is the u-boot binary

## Other notes

### Quilt

This repository is managed using quilt
https://wiki.debian.org/UsingQuilt

if you want to rollback the patches you can run
```
quilt pop -a
```

### Making edits

```
quilt series
quilt push patches/1.5GB_OPZ3_fix.patch
vi u-boot/arch/arm/mach-sunxi/dram_sun50i_h616.c <- or use any editor you prefer
quilt refresh <- note this would update patches/1.5GB_OPZ3_fix.patch
quilt push -a <- this applies the remaining of the patches
# compile it
cd arm-trusted-firmware
bash arm-trust-fw-make.sh <- normally only need to be done once, not necessary if that is already built prior
cd u-boot
bash build.sh                           
# test it if necessary
# you can rollback all the patches using 
# quilt pop -a
```
