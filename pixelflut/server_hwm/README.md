This server version uses ansyncio and therefore python 3.4 is needed.

Install pygame and other depencies for python3 in an virtual env (Mint/Ubuntu)
------------------------------------------------------------------------------

```bash
virtualenv -p python3 env

. ./env/bin/activate

sudo apt-get install python3-dev libsdl-image1.2-dev libsdl-mixer1.2-dev \
libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion \
libportmidi-dev libfreetype6-dev

svn co svn://seul.org/svn/pygame/trunk pygame
cd pygame
python setup.py build
python setup.py install

pip install docopt
```
