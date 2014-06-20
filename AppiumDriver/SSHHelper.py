'''
Created on May 16, 2014

@author: yuliu
'''
import paramiko,traceback
from subprocess import Popen,PIPE,STDOUT
import socket
import sys
import threading

def check_ip(ip):
    local_name = socket.gethostname()
    local_ip = socket.gethostbyname(local_name)
    if ip.find(local_name) == 0:
        ip = ip.replace(local_name, "localhost")
    if ip.find(local_ip) == 0:
        ip = ip.replace(local_ip, "localhost")
    return ip

class SSHError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message) 

class SSHHelper:
    def __init__(self, ip = None, host_name = '', host_pwd = ''):
        self.ip = check_ip(ip)
        self.host_name = host_name
        self.host_pwd = host_pwd
        self.ssh = None
        
    def connect(self):
        if not self.ssh and self.ip.find("localhost")!=0:
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.ip, username = self.host_name, password = self.host_pwd)
            except  paramiko.AuthenticationException:
                print "Authentication failed when connecting to %s" % self.host
                sys.exit(1)
            except Exception,e :
                traceback.print_exc()
                raise SSHError('cannot ssh connect to %s. error happens %s' %(self.ip,str(e)))
        else:
            print "Localhost doesn't need to connect"
            
    def disconnect(self):
        if self.ssh and self.ip.find("localhost")!=0:
            try:
                self.ssh.close()
                self.ssh = None
            except Exception,e :
                traceback.print_exc()
                raise SSHError('cannot ssh disconnect to device. %s' %(str(e)))
        else:
            print "Localhost doesn't need to disconnect"
    
    def exe_cmd(self, cmd = '', logfile = None):
        if self.ssh and self.ip.find("localhost")!=0:
            print cmd
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            del stdin
            return stdout, stderr
        elif self.ip.find("localhost")==0:
            print cmd
            std_out = logfile if logfile else PIPE
            if sys.platform.find("win")==0:
                self.proc = Popen(cmd,shell=True,stdin=PIPE,stdout=std_out,stderr=STDOUT)
            else:
                self.proc = Popen(cmd,stdin=PIPE,stdout=std_out,stderr=STDOUT)
            return self.proc