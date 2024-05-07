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

