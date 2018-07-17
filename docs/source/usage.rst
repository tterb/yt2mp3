Usage
=====

The program can be executed via the as follows:

.. code:: bash
  
  yt2mp3 [-options]

Options
--------------

+----------------------+----------------------------------------------+
| ``-t, --track``     | Specify the track name query             |
+----------------------+----------------------------------------------+
| ``-a, --artist``    | Specify the artist name query            |
+----------------------+----------------------------------------------+
| ``-u, --url``       | Specify a Youtube URL or ID              |
+----------------------+----------------------------------------------+
| ``-p, --playlist``  | Specify a Youtube playlist URL or ID     |
+----------------------+----------------------------------------------+
| ``-o, --overwrite`` | Overwrite the file if one exists in output directory  |
+----------------------+----------------------------------------------+
| ``-q, --quiet``     | Suppress program command-line output     |
+----------------------+----------------------------------------------+
| ``-v, --verbose``   | Display a command-line progress bar     |
+----------------------+----------------------------------------------+
| ``--version``       | Show the version number and exit         |
+----------------------+----------------------------------------------+
| ``-h, --help``      | Display  information on usage and functionality  |
+----------------------+----------------------------------------------+

***Note:*** Displaying the progress bar currently has a significant impact on download performance, due to \#180_.  

.. _180: https://github.com/nficano/pytube/issues/180

________________________________

|terminal|

.. |terminal| image:: images/terminal.gif
  :alt: Usage Example
