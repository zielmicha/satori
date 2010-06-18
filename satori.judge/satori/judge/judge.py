# vim:ts=4:sts=4:sw=4:expandtab
"""Satori judge implementation.
"""

from satori.objects import Object, Argument
import BaseHTTPServer
import cgi
from multiprocessing import Process, Pipe
import os
import prctl
import shutil
import signal
import subprocess
import time
import unshare
import yaml


def loopUnmount(root):
    while True:
        paths = []
        with open('/proc/mounts', 'r') as mounts:
            for mount in mounts:
                path = mount.split(' ')[1]
                if checkSubPath(os.path.join('/', root), path):
                    paths.append(path)
            if len(paths) == 0:
                break
            paths.sort()
            paths.reverse()
            for path in paths:
                subprocess.call(['umount', '-l', path])

def checkSubPath(root, path):
    root = os.path.realpath(root).split('/')
    path = os.path.realpath(path).split('/')

    if len(path) < len(root):
    	return False
    for i in range(0, len(root)):
        if root[i] != path[i]:
        	return False
    return True

def jailPath(root, path):
    return os.path.join(root, os.path.abspath(path)[1:])

class JailExec(Object):
    @Argument('root', type=str, default='/jail')
    @Argument('path', type=str)
    @Argument('args', default=[])
    @Argument('search', type=bool, default=False)
    def __init__(self, root, path, args, search):
        self.root = root
        self.path = path
        self.args = [self.path] + args
        self.search = search

    def run(self):
        os.chroot(self.root)
        os.chdir('/')
        if self.search:
            os.execvp(self.path, self.args)
        else:
            os.execv(self.path, self.args)

class JailRun(Object):
    oldroot = '__oldroot__'

    @Argument('root', type=str, default='/jail')
    @Argument('path', type=str)
    @Argument('args', default=[])
    @Argument('search', type=bool, default=False)
    def __init__(self, root, path, args, search):
        self.root = root
        self.path = path
        self.args = [self.path] + args
        self.search = search

    def child(self, pipe):
        try:
            unshare.unshare(unshare.CLONE_NEWNS | unshare.CLONE_NEWUTS | unshare.CLONE_NEWIPC | unshare.CLONE_NEWNET)

            pipe.send(1)
#WAIT FOR PARENT CREATE VETH
            pipe.recv()
            subprocess.check_call(['ifconfig', 'vethsg', '192.168.100.102/24', 'up'])
            subprocess.check_call(['route', 'add', 'default', 'gw', '192.168.100.101'])
            subprocess.check_call(['ifconfig', 'lo', '127.0.0.1/8', 'up'])
            subprocess.check_call(['iptables', '-t', 'filter', '-F'])
            subprocess.check_call(['iptables', '-t', 'nat', '-F'])
            subprocess.check_call(['iptables', '-A', 'INPUT', '-i', 'lo', '-j', 'ACCEPT'])
            subprocess.check_call(['iptables', '-A', 'INPUT', '-m', 'state', '--state', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'])
            subprocess.check_call(['iptables', '-A', 'INPUT', '-m', 'state', '--state', 'INVALID', '-j', 'DROP'])
            subprocess.check_call(['iptables', '-P', 'INPUT', 'DROP'])
            subprocess.check_call(['iptables', '-A', 'OUTPUT', '-o', 'lo', '-j', 'ACCEPT'])
            subprocess.check_call(['iptables', '-A', 'OUTPUT', '-m', 'state', '--state', 'ESTABLISHED,RELATED', '-j', 'ACCEPT'])
            subprocess.check_call(['iptables', '-A', 'OUTPUT', '-m', 'state', '--state', 'INVALID', '-j', 'DROP'])
            subprocess.check_call(['iptables', '-A', 'OUTPUT', '-m', 'owner', '--uid-owner', 'root', '-j', 'ACCEPT'])
            subprocess.check_call(['iptables', '-P', 'OUTPUT', 'DROP'])
            subprocess.check_call(['iptables', '-P', 'FORWARD', 'DROP'])
            subprocess.check_call(['iptables', '-t', 'nat', '-P', 'PREROUTING', 'ACCEPT'])
            subprocess.check_call(['iptables', '-t', 'nat', '-P', 'POSTROUTING', 'ACCEPT'])
            subprocess.check_call(['iptables', '-t', 'nat', '-P', 'OUTPUT', 'ACCEPT'])

            pipe.send(1)
#WAIT FOR PARENT CLEANUP
    		pipe.recv()
	    	pipe.close()

	    	runargs = [ 'runner', '--debug', '/runner.debug.txt', '--root', self.root, '--pivot', '--ns-ipc', '--ns-uts', '--ns-pid', '--ns-mount', '--cap', 'safe', ]
            if self.search:
            	runargs.append('--search')
            runargs += self.args
            print runargs
            os.execvp('runner', runargs)
        except:
            raise
    	finally:
	    	pipe.close()

    def parent(self):
        subprocess.check_call(['mount', '--make-rshared', self.root])
        pipe, pipec = Pipe()
        try:
            child = Process(target = self.child, args=(pipec,))
            child.start()
#WAIT FOR CHILD START AND UNSHARE
            pipe.recv()
            subprocess.check_call(['ip', 'link', 'add', 'name', 'vethsh', 'type', 'veth', 'peer', 'name', 'vethsg'])
            subprocess.check_call(['ifconfig', 'vethsh', '192.168.100.101/24', 'up'])
            subprocess.check_call(['ip', 'link', 'set', 'vethsg', 'netns', str(child.pid)])
            pipe.send(1)
#WAIT FOR CHILD CONFIGURE NETWORK AND PIVOT ROOT
    		pipe.recv()
            pipe.send(1)
        except:
            raise
        finally:
            pipe.close()
        child.join()

    def run(self):
        self.parent()


class JailBuilder(Object):
    safePath = '/cdrom'
    safeExtension = '.template'
    scriptTimeout = 5

    @Argument('root', type=str, default='/jail')
    @Argument('template', type=str, default='/cdrom/jail.template')
    def __init__(self, root, template):
        if not checkSubPath(self.safePath, template) or os.path.splitext(template)[1] != self.safeExtension:
        	raise Exception('Template '+template+' is not safe')
        self.root = root
        self.template = template

    def create(self):
        try:
            os.mkdir(self.root)
            template = yaml.load(open(self.template, 'r'))
            dirlist = []
            quota = 0
            num = 1
            if 'base' in template:
                for base in template['base']:
                    if isinstance(base, str):
                        base = { 'path' : base }
                	opts = base.get('opts', '')
                	name = base.get('name', '__' + str(num) + '__')
                	num += 1
                    path = os.path.join(self.root, os.path.basename(name))
                    if 'path' in base:
                        type = base.get('type')
                        src = os.path.realpath(base['path'])
                        if os.path.isdir(src):
                            os.mkdir(path)
                            subprocess.check_call(['mount', '-o', 'bind,ro,'+opts, src, path])
                            dirlist.append(path + '=nfsro')
                        elif os.path.isfile(src):
                            os.mkdir(path)
                            if type is None:
                            	ext = os.path.splitext(src)[1]
                                if ext:
                                    type = ext[1:]
                                else:
                                	type = 'auto'
                            subprocess.check_call(['mount', '-t', type, '-o', 'loop,noatime,ro,'+opts, src, path])
                            dirlist.append(path + '=nfsro')
                        else:
                        	raise Exception('Path '+base['path']+' can\'t be mounted')
            if 'quota' in template:
                quota = int(template['quota'])
            if quota > 0:
                path = os.path.join(self.root, '__rw__')
                os.mkdir(path)
                subprocess.check_call(['mount', '-t', 'tmpfs', '-o', 'noatime,rw,size=' + str(quota) + 'm', 'tmpfs', path])
                dirlist.append(path + '=rw')
            dirlist.reverse()
            subprocess.check_call(['mount', '-t', 'aufs', '-o', 'noatime,rw,dirs=' + ':'.join(dirlist), 'aufs', self.root])
            if 'insert' in template: 
                for src in template['insert']:
                	src = os.path.realpath(src)
                    if os.path.isdir(src):
                    	subprocess.check_call(['rsync', '-a', src, self.root])
                    elif os.path.isfile(src):
                        name = os.path.basename(src).split('.')
                        if name[-1] == 'zip':
                        	subprocess.check_call(['unzip', '-d', self.root, src])
                        elif name[-1] == 'tar':
                        	subprocess.check_call(['tar', '-C', self.root, '-x', '-f', src])
                        elif name[-1] == 'tbz' or name[-1] == 'tbz2' or (name[-1] == 'bz' or name[-1] == 'bz2') and name[-2] == 'tar':
                        	subprocess.check_call(['tar', '-C', self.root, '-x', '-j', '-f', src])
                        elif name[-1] == 'tgz'  or name[-1] == 'gz' and name[-2] == 'tar':
                        	subprocess.check_call(['tar', '-C', self.root, '-x', '-z', '-f', src])
                        elif name[-1] == 'lzma' and name[-2] == 'tar':
                        	subprocess.check_call(['tar', '-C', self.root, '-x', '--lzma', '-f', src])
                        else:
                        	raise Exception('Path '+src+ ' can\'t be inserted')
                    else:
                        raise Exception('Path '+src+ ' can\'t be inserted')
            if 'remove' in template:
                for path in template['remove']:
                	subprocess.check_call(['rm', '-rf', jailPath(self.root, path)])
            if 'bind' in template:
                for bind in template['bind']:
                    if isinstance(bind, str):
                        bind = { 'src' : bind }
            		src = os.path.realpath(bind['src'])
            		dst = jailPath(self.root, bind.get('dst',src))
                	opts = bind.get('opts', '')
                	rec = bind.get('recursive', 0)
                    if rec:
                    	rec = 'rbind'
                    else:
                    	rec = 'bind'
                    subprocess.check_call(['mount', '-o', rec + ',' + opts, src, dst])
            if 'script' in template:
                for script in template['script']:
                	params = script.split(' ')
                    runner = JailExec(root=self.root, path=params[0], args=params[1:], search=True)
                    process = Process(target=runner.run)
                    process.start()
                    process.join(self.scriptTimeout)
                    if process.is_alive():
                    	process.terminate()
                    	raise Exception('Script '+script+' failed to finish before timeout')
                    if process.exitcode != 0:
                    	raise Exception('Script '+script+' returned '+str(process.exitcode))
        except:
            self.destroy()
            raise

    def destroy(self):
        loopUnmount(self.root)
        shutil.rmtree(self.root)



class JailHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_POST(self):
        s = self.rfile.read(int(self.headers['Content-Length']))
        input = yaml.load(s)
        cmd = 'cmd_' + self.path[1:]
        try:
            output = getattr(self, cmd)(input)
            self.send_response(200)
            self.send_header("Content-type", "text/yaml; charset=utf-8")
            self.end_headers()
            yaml.dump(output, self.wfile)
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(ex))
    def cmd_GETSUBMIT(self, input):
        #TODO: Thrift get data
        output = {}
        output['id'] = self.submit_id
        return output
    def cmd_GETTEST(self, input):
        #TODO: Thrift get data
        output = {}
        output['id'] = self.test_id
        return output
    def cmd_GETCACHE(self, input):
        hash = gen_hash(input['what'])
        fname = jailPath(self.root_path, input['where'])
        #TODO: Przeszukac cache
        return 'OK'
    def cmd_PUTCACHE(self, input):
        hash = gen_hash(input['what'])
        fname = jailPath(self.root_path, input['where'])
        type = input['how']
        #TODO: Handle cache
        return 'OK'
    def cmd_GETBLOB(self, input):
        hash = input['hash']
        fname = jailPath(self.root_path, input['where'])
        #TODO: Thrift get blob
        return 'OK'
    def cmd_CREATECG(self, input):
        path = jailPath(self.cg_root, input['path'])
        os.mkdir(path)
        return 'OK'
    def cmd_LIMITCG(self, input):
        path = jailPath(self.cg_root, input['path'])
        def set_limit(type, value):
            file = os.path.join(path, type)
            with open(file, 'w') as f:
                f.write(str(value))
        if 'memory' in input:
        	set_limit('memory.limit_in_bytes', int(input['memory']))
        return 'OK'
    def cmd_ASSIGNCG(self, input):
        path = jailPath(self.cg_root, input['path'])
        file = jailPath(self.root_path, input['file'])
        pid = int((subprocess.Popen(["fuser", file], stdout=subprocess.PIPE).communicate()[0]).split(':')[-1])
        #TODO: Check pid
        print 'Gotya ', pid
        with open(os.path.join(path, 'tasks'), 'w') as f:
            f.write(str(pid))
        return 'OK'
    def cmd_DESTROYCG(self, input):
        path = os.path.join(jailPath(self.cg_root, input['path']))
        killer = True
        #TODO: po ilu probach sie poddac?
        while killer:
        	killer = False
            with open(os.path.join(path, 'tasks'), 'r') as f:
                for pid in f:
                	killer = True
                	os.kill(int(pid), signal.SIGKILL)
            time.sleep(1)
        return 'OK'
    def cmd_QUERYCG(self, input):
        path = os.path.join(jailPath(self.cg_root, input['path']))
        output = {}
        with open(os.path.join(path, 'cpuacct.stat'), 'r') as f:
            _, output['cpu.user'] = f.readline().split()
            _, output['cpu.system'] = f.readline().split()
        with open(os.path.join(path, 'memory.max_usage_in_bytes'), 'r') as f:
            output['memory'] = f.readline()
        return output

    def cmd_CREATEJAIL(self, input):
        path = os.path.join(jailPath(self.root_path, input['path']))
        template = input['template']
        jb = JailBuilder(root=path, template=template)
        jb.create()

    def cmd_DESTROYJAIL(self, input):
        path = os.path.join(jailPath(self.root_path, input['path']))
        jb = JailBuilder(root=path)
        jb.destroy()









def create_handler(submit, test, root, cgroot):
    class Handler(JailHandler):
        def __init__(self, *args, **kwargs):
            self.submit_id = submit
            self.test_id = test
            self.root_path = root
            self.cg_root = cgroot
            JailHandler.__init__(self, *args, **kwargs)
    return Handler


def run_server(host, port):
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((host, port), create_handler(1, 2, '/jail', '/cg'))
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()



if __name__ == "__main__":
	from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] DIR")
	parser.add_option("-D", "--destroy",
	    default=False,
	    action="store_true",
	    help="Destroy created chroot")
	parser.add_option("-S", "--server",
	    default=False,
	    action="store_true",
	    help="Run server")
	(options, args) = parser.parse_args()

	path = args[0]
	temp = args[1]

    jb = JailBuilder(root=path, template=temp)
    if options.destroy:
    	jb.destroy()
    elif options.server:
        run_server('127.0.0.1', 8765)
    else:
    	jb.create()
    	jr = JailRun(root=path, path='bash', search=True) 
    	jr.run()