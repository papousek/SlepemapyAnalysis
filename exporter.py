# -*- coding: utf-8 -*-

import paramiko
from scp import SCPClient
from os import path,listdir

'''used for export of index.html and visualisation files to faculty server
'''
class Exporter():
    '''generates very simple html with all svg pictures attached
    '''
    def generate_index_html(self,path):
        with open(path+'\\index.html','w+') as index:
            index.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>Statistics generated from blind maps</title>\n<//head>\n<body>\n')
                
            svg = listdir(path+'/graphs/')
            for graph in svg:
                index.write("<img src=\".\\graphs\\"+graph+"\">\n")
    
            svg = listdir(path+'/maps/')
            for map in svg:
                index.write("<img src=\".\\maps\\"+map+"\">\n")

            index.write('</body>\n</html>')

    @staticmethod
    def _sendFile(scp,file,destination):  
        scp.put(file, remote_path = destination) 

    def export(self, directory,user,pw):
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('aisa.fi.muni.cz',username=user,password=pw)
            
            #clean out stats from yesterday
            ssh.exec_command('rm -f ~/public_html/index.html') #clears old index.html
            ssh.exec_command('find ~/public_html/graphs/ -type f -delete') #deletes contents of graph dir
            ssh.exec_command('find ~/public_html/maps/ -type f -delete') #deletes contents of map dir
            
            #prepare and send index page
            scp = SCPClient(ssh.get_transport())  
            self._sendFile(scp,directory+'/index.html','~/public_html/index.html')
            ssh.exec_command('setfacl -m u:apachefi:r-- ~/public_html/index.html')
            
            #send all other files
            svg = listdir(directory+'/graphs/')
            for graph in svg:
                self._sendFile(scp,directory+'/graphs/'+graph,'~/public_html/graphs/')
            svg = listdir(directory+'/maps/')
            for map in svg:
                self._sendFile(scp,directory+'/maps/'+map,'~/public_html/maps/')
        finally:
            if ssh:
                ssh.close()