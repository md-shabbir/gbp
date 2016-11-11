import subprocess

#cmd = "sudo ip netns exec nfp-proxy ssh -i ~/configurator_key.pem root@172.16.0.3 docker exec -d radius_configurator service nfp-pecan restart"
cmd = "sudo ip netns exec nfp-proxy ssh -i ~/configurator_key.pem root@172.16.0.3 docker ps -q"
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
(stdout, stderr) = proc.communicate()

if proc.returncode:
    print "Error in getting docker id"
    print stderr
else:
    docker_id = stdout.strip()
    print 'docker id: %s' % docker_id
    cmd = "sudo ip netns exec nfp-proxy"
    cmd += " ssh -i ~/configurator_key.pem root@172.16.0.3"
    cmd += " docker exec " + docker_id + " service nfp-pecan restart"
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = proc.communicate()
    print 'out: ', stdout
    print 'err: ', stderr
    if proc.returncode:
        print "Error in pecan start"
        print stderr
    else:
        print 'pecan restarted'


"""if stderr:
    LOG.error(stderr)
    print "Error in pecan restart"
    print stderr
else:
    LOG.debug("configurator restarted")
    print stdout
    print "success" 
"""

