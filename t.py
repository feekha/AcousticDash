'''

import pysftp as sftp


class My_Connection(sftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)

with sftp.Connection('us-securetransfer.dnv.com' , 'measurementsne' , 'yerD!Hvdt8n5ysh!t') as pythonsftp:
    print("succesful")

'''


'''

import paramiko

command = "ls"

# Update the next three lines with your
# server's information

host = "us-securetransfer.dnv.com"
username = "measurementsne"
password = "yerD!Hvdt8n5ysh!t"

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port = 22, username=username, password=password,key_filename='measurementsneprivate.ppk')
print(client)

sftpp = client.open_sftp()

print(sftpp)
#_stdin, _stdout,_stderr = client.exec_command("ls")
#print(_stdout.read().decode())
#client.close()

'''

import paramiko.ssh_exception
import paramiko

host = "us-securetransfer.dnv.com"                    #hard-coded
port = 22

password = "yerD!Hvdt8n5ysh!t"                #hard-coded
username = "measurementsne"  

def handler(title, instructions, fields):
    if len(fields) > 1:
        raise paramiko.SSHException("Expecting one field only.")
    return [password]

transport = paramiko.Transport(host , port) 
transport.connect(username='measurementsne')
transport.auth_interactive(username, handler)
              #hard-coded
#transport.connect(username = username, password = password)

print(transport)

#sftp = paramiko.SFTPClient.from_transport(transport)

#import sys
#path = './THETARGETDIRECTORY/' + sys.argv[1]    #hard-coded
#localpath = sys.argv[1]
#sftp.put(localpath, path)

#sftp.close()
#transport.close()
#print 'Upload done.'




'''


from paramiko import Transport, SFTPClient, RSAKey
key = RSAKey(filename='id_rsa')
con = Transport('us-securetransfer.dnv.com', 22)
con.connect(username='measurementsne', password='yerD!Hvdt8n5ysh!t')
print(con)
sftp = SFTPClient.from_transport(con)
#sftp.listdir(path='.')



from paramiko import Transport, SFTPClient, RSAKey

import paramiko
k = paramiko.RSAKey.from_private_key_file("id_rsa")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("connecting")
c.connect( hostname = "us-securetransfer.dnv.com", username = "measurementsne", password='yerD!Hvdt8n5ysh!t',allow_agent=False,look_for_keys=False)
print("connected" , c)

_stdin, _stdout,_stderr = c.exec_command("ls -l")
output = _stdout.read()
print(output)

'''