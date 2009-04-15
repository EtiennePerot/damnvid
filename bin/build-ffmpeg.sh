#!/bin/sh

sudo mkdir /ffmpeg
sudo chmod 0777 /ffmpeg
prefix="$HOME/ffmpeg/libs/compiled"
rm -rf ~/ffmpeg
mkdir ~/ffmpeg
cd ~/ffmpeg
mkdir libs
cd libs
mkdir compiled
wget http://downloads.sourceforge.net/faac/faad2-2.7.tar.gz
tar -xf faad2*.tar.gz
rm -rf faad2*.tar.gz
cd faad2*
./configure --enable-static --prefix=$prefix
make
make install
cd ..
wget http://downloads.sourceforge.net/faac/faac-1.28.tar.gz
tar -xf faac*.tar.gz
rm -rf faac*.tar.gz
cd faac*
./configure --enable-static --prefix=$prefix
make
make install
cd ..
wget http://downloads.xvid.org/downloads/xvidcore-1.2.1.tar.gz
tar -xf xvid*.tar.gz
rm -rf xvid*.tar.gz
cd xvid*
# Just try to cd again:
cd xvid*
cd build/generic
./configure --prefix=$prefix
make
make install
cd ~/ffmpeg/libs
git clone git://git.videolan.org/x264.git
cd x264
./configure --prefix=$prefix
make
make install
cd ..
wget http://softlayer.dl.sourceforge.net/sourceforge/lame/lame-3.97.tar.gz
tar -xf lame*.tar.gz
rm -rf lame*.tar.gz
cd lame*
./configure --enable-static --prefix=$prefix
make
make install
cd ..
svn co http://svn.xiph.org/trunk/ogg ogg
svn co http://svn.xiph.org/trunk/theora theora
svn co http://svn.xiph.org/trunk/vorbis vorbis
cd ogg
./autogen.sh --prefix=$prefix
make
make install
cd ../theora
./autogen.sh --prefix=$prefix
make
make install
cd ../vorbis
./autogen.sh --prefix=$prefix
make
make install
cd ~/ffmpeg
libprefix="/ffmpeg"
sudo cp libs/compiled/lib/*.a $libprefix/
svn co svn://svn.ffmpeg.org/ffmpeg/trunk ffmpeg
cd ffmpeg
./configure --enable-memalign-hack --enable-libxvid --enable-libx264 --enable-libfaac --enable-libfaad --enable-libmp3lame --enable-libvorbis --enable-libtheora --enable-pthreads --enable-gpl --enable-postproc --enable-static --disable-shared --extra-cflags=--static --disable-ffplay --disable-ffserver --extra-libs=$libprefix/libfaac.a --extra-libs=$libprefix/libfaad.a --extra-libs=$libprefix/libmp3lame.a --extra-libs=$libprefix/libmp4ff.a --extra-libs=$libprefix/libogg.a --extra-libs=$libprefix/libx264.a --extra-libs=$libprefix/libxvidcore.a --extra-libs=$libprefix/libogg.a --extra-libs=$libprefix/libtheora.a --extra-libs=$libprefix/libvorbis.a
make
mv ./ffmpeg ~/ffmpeg-bin
cd ~
rm -rf ./ffmpeg
mv ./ffmpeg-bin ./ffmpeg
upx --brute ./ffmpeg
rm -rf /ffmpeg
echo "All done! ffmpeg has been moved to $HOME."
