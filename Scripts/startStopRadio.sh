
cd /home/pi/rtl_fm_python
./rtl_fm_python_web.py -s 200000 -r 48000 -M wbfm -f 88.1M - |aplay -D plughw:1,0 -r 32000 -f S16_LE -t raw -c 1 
