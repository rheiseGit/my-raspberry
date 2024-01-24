# my-raspberry
The project aims to create a web application for a Raspberry Pi, which provides various functions. The app should enable easy integration of additional functions.

## My Installation @ Raspberry

-	Raspberry Pi 4 B

-	Raspberry-Pi-OS (Bookworm)

-	enviroment manager Miniconda

	> wget http://repo.continuum.io/miniconda/Miniconda3-py39_4.9.2-Linux-aarch64.sh

- some commandos

	> conda env create -n myrpi python=3.11.4

	> conda activate myrpi

	> conda install --file requirement.txt

	> conda install -c conda-forge opencv

	> conda install -c conda-forge dash

	> conda install -c conda-forge pandas

	> conda env export > environment.yml
