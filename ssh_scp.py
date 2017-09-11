# -*- coding: utf-8 -*-
# !/usr/bin/python
import paramiko
import threading
import optparse
from scp import SCPClient

screenLock=threading.Semaphore(value=1)


def scpfile(ssh, file, dfil):
    scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
    remotepath = dfil
    localpath = file
    try:
        scpclient.put(localpath, remotepath)
        return '[*] Upload %s to %s  OK ' % (file, dfil)
    except:
        return '[*] Upload %s to %s  Error ' % (file, dfil)
        # localpath1 = 'get.txt'
        # scpclient.get(remotepath, localpath1)  # 从服务器中获取文件


def ssh2(ip, username, passwd, cmd, scp, dfile):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        outstr=[]
        outstr.append('%s:' % (ip))
        for m in cmd:
            stdin, stdout, stderr = ssh.exec_command(m)
            out = stdout.readlines()
            for o in out:
                outstr.append(o)
        if scp != None:
            for i in scp:
                outstr.append(scpfile(ssh, i, dfile))
        screenLock.acquire()
        for i in outstr:
            print i.strip('\n')
        screenLock.release()

        ssh.close()
    except:
        pass


def testpw(hosts, username, passwords, cmds, scp, dfile):
    for i in hosts:
        for j in passwords:
            a = threading.Thread(target=ssh2, args=(i, username, j, cmds, scp, dfile))
            a.start()


if __name__ == '__main__':
    
    parse = optparse.OptionParser(
        '''
%prog -H <Host> -f <Host File> -u <User> -p <Password> -P  <Password File> -c <Command> --scp <file> -d <des file>

  eg: %prog -H 192.168.1.1,192.168.1.2 -u root -p password -c hostname
      %prog -f hostfile -u root -p password -c hostname
      %prog -H 192.168.1.1 -u root -p password --scp file -d /tmp/
        ''')
    parse.add_option('-u', dest='user', type='string', default='root', help='specify the username ')
    parse.add_option('-H', dest='tHost', type='string', help='specify the target address split by \',\'')
    parse.add_option('-f', dest='tHfile', type='string', help='specify the target address file')
    parse.add_option('-p', dest='passwd', type='string', help='password for host split by \',\'')
    parse.add_option('-P', dest='pwfile', type='string', help='password file for host')
    parse.add_option('-c', dest='cmd', type='string', help='command split by \';\'')
    parse.add_option('--scp', dest='scp', type='string', help='cp file host , file split by \',\'')
    parse.add_option('-d', dest='dfile', type='string', default='None',
                     help='scp file to host:dfile ,default file is user\'s home ')
    
    (option, args) = parse.parse_args()
    if (option.tHost == None) & (option.tHfile == None):
        print '[-] Not target Host'
        print parse.usage
        exit(0)
    if (option.passwd == None) & (option.pwfile == None):
        print '[-] Not password for connect'
        print parse.usage
        exit(0)
    
    host = []
    password = []
    cmd = []
    scp = []
    dfile = option.dfile
    user = option.user
    if option.tHost != None:
        for i in option.tHost.split(','):
            host.append(i)
    if option.passwd != None:
        for i in option.passwd.split(','):
            password.append(i)
    if option.cmd != None:
        for i in option.cmd.split(';'):
            cmd.append(i)
    if option.scp != None:
        for i in option.scp.split(','):
            scp.append(i)
    if dfile == 'None':
        dfile = '/tmp/'
    if option.tHfile != None:
        try:
            with open(option.tHfile, 'r') as f:
                for i in f.readlines():
                    host.append(i.split('\n')[0])
        except:
            print '[-] Open Host file fales.'
            exit(0)
    if option.pwfile != None:
        try:
            with open(option.pwfile, 'r') as f:
                for i in f.readlines():
                    password.append(i.split('\n')[0])
        except:
            print '[-] Open Password file fales.'
            exit(0)
    testpw(host, user, password, cmd, scp, dfile)
