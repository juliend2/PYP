# Autoreloading launcher.
# Most of this code is borrowed from the Django project (http://www.djangoproject.com).
# Django borrowed if from Peter Hunt and the CherryPy project 
# (http://www.cherrypy.org).
# Some taken from Ian Bicking's Paste (http://pythonpaste.org/).
#
# Portions copyright (c) 2004, CherryPy Team (team@cherrypy.org)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of the CherryPy Team nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import os, sys, time
import fnmatch
import compiler
import py2php

try:
    import thread
except ImportError:
    import dummy_thread as thread

# This import does nothing, but it's necessary to avoid some race conditions
# in the threading module. See http://code.djangoproject.com/ticket/2330 .
try:
    import threading
except ImportError:
    pass


RUN_RELOADER = True

_mtimes = {}
_win = (sys.platform == "win32")


class GlobDirectoryWalker:
    # a forward iterator that traverses a directory tree

    def __init__(self, directory, pattern="*"):
        self.stack = [directory]
        self.pattern = pattern
        self.files = []
        self.index = 0

    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if ( os.path.isdir(fullname) and not os.path.islink(fullname)
                and not fullname.endswith('.git') and not fullname.endswith('.AppleDouble')):
                    self.stack.append(fullname)
                if fnmatch.fnmatch(file, self.pattern):
                    return fullname

def process(source_path, dest_path):
    print 'updating the PHP files.'
    for file in GlobDirectoryWalker(source_path, "*.py?"):
        if file.endswith('.pyc'): # skip the .pyc files
            continue
        (source_filepath, source_filename) = os.path.split(file)
        (source_shortname, source_extension) = os.path.splitext(source_filename)
        if source_shortname.startswith('._'):
            continue
        if file.endswith('.py'):
            unindented_source = py2php.get_source(compiler.parseFile(file))
            phpcode = py2php.indent_source(py2php.add_semicolons(unindented_source))       
        else: # .pyp file
            print 'ELSE'
            reg = re.compile('(<\?pyp.*?\?>)', re.S) # trouver les <?pyp .. ?>
            matched = reg.split(open(file).read())
            phpcode = ''
            for match in matched:
                if match.startswith('<?pyp') and match.endswith('?>'):
                    pypCode = match[5:-2]
                    print 'pypCode', pypCode
                    unindented_source = py2php.get_source(compiler.parse(pypCode))
                    phpcode += py2php.indent_source(py2php.add_semicolons(unindented_source))
                else:
                    phpcode += match
        directories = source_filepath[len(sys.argv[1]):]
        # create the subdirectories :
        try :
            os.makedirs(dest_path + '/' + directories)
        except OSError:
            pass
        if len(directories) > 0:
            dir_file = directories + '/' + source_shortname
        else:
            dir_file = source_shortname
        phpfile = open(dest_path +'/'+ dir_file + '.php', 'w')
        phpfile.write( phpcode ) # write the converted code
        phpfile.close()

def code_changed(source_path):
    global _mtimes, _win
    for filename in GlobDirectoryWalker(source_path, "*.py"):
        if filename.endswith(".pyc") or filename.endswith(".pyo"):
            filename = filename[:-1]
        if not os.path.exists(filename):
            continue # File might be in an egg, so it can't be reloaded.
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes:
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes[filename]:
            _mtimes = {}
            return True
    return False

def reloader_thread(source_path):
    while RUN_RELOADER:
        if code_changed(source_path):
            sys.exit(3) # force reload
        time.sleep(1)

def restart_with_reloader():
    while True:
        args = [sys.executable] + sys.argv
        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ["RUN_MAIN"] = 'true'
        exit_code = os.spawnve(os.P_WAIT, sys.executable, args, new_environ)
        if exit_code != 3:
            return exit_code

def python_reloader(main_func, args, kwargs):
    if os.environ.get("RUN_MAIN") == "true":
        thread.start_new_thread(main_func, args, kwargs)
        try:
            reloader_thread(args[0])
        except KeyboardInterrupt:
            pass
    else:
        try:
            sys.exit(restart_with_reloader())
        except KeyboardInterrupt:
            pass

def main(main_func, args=None, kwargs=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    python_reloader(main_func, args, kwargs)

main(process, (sys.argv[1],sys.argv[2]))
