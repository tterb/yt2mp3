=================
Additional Setup
=================

The project utilizes the `pydub <https://github.com/jiaaro/pydub>`_ package for audio-file manipulation, which requires that a multimedia decoding library to function properly.  
You can use `ffmpeg <http://ffmpeg.org/>`_ or `libav <https://www.libav.org/>`_.


Mac (using `homebrew <http://brew.sh/>`_)
-------------------------------------------

.. code:: bash

  # ffmpeg
  brew install ffmpeg --with-libvorbis --with-sdl2 --with-theora
  
  ####    OR    #####
  
  # libav
  brew install libav --with-libvorbis --with-sdl --with-theora


Linux (using `aptitude <https://wiki.debian.org/Aptitude>`_)
--------------------------------------------------------------

.. code:: bash

  # libav
  apt-get install libav-tools libavcodec-extra-53

  ####    OR    #####

  # ffmpeg
  apt-get install ffmpeg libavcodec-extra-53


Windows
---------

  * Download and extract **libav** from Windows binaries `provided here <http://builds.libav.org/windows/>`_.
  * Add the **libav** `/bin` folder to your PATH

|
