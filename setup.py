#!/usr/bin/env python

import distutils.core 
import distutils.dir_util
import distutils.sysconfig
import os
import shutil
import tempfile

package_root = distutils.sysconfig.get_python_lib() 
package_name = 'airtorrent'

# TODO more thoroughly check permissions
dst_dir = os.path.join(package_root, 'miro', 'frontends', package_name)
try:
    os.mkdir(dst_dir)
except OSError:
    shutil.rmtree(dst_dir)
    os.mkdir(dst_dir)
    pass

server_code_files = ['application.py', 'hls_server.py', 'miro_library_manager.py',
                     'torrent_download_manager.py', 'torrent_session_manager.py']

web_code_files = ['web.py']
       
for code_file in server_code_files:
    code_file = os.path.join('server', code_file)
    shutil.copy(code_file, dst_dir)

for code_file in web_code_files:
    code_file = os.path.join('web', code_file)
    shutil.copy(code_file, dst_dir)

#distutils.core.setup(name=package_name,
#    version='0.0',
#    description='AirTorrent HLS Server',
#    author='Jordan Schneider',
#    author_email='jbschne@umich.edu',
#    url='http://airtorrent.github.com',
#    py_modules=[package_name]
#    #py_modules=['airtorrent.application', 'airtorrent.hls_server', 'airtorrent.miro_library_manager',
#    #          'airtorrent.setup', 'airtorrent.torrent_download_manager', 'airtorrent.torrent_session_manager',
#    #          'airtorrent.test_setup']
#    )



