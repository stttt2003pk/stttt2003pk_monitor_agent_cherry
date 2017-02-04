# stttt2003pk_monitor_agent

## Introduction

**stttt2003pk_monitor_agent** is some python program running in the server the gather the server information and handle them

```
From my work i have a lot of time to make some program the information of the service running on the server.
I ve made a lot agent monitorring the service like LVS(keepalived)/f5/nginx/haproxy/sunrunIaas(production in my company rebuild kvm libvirt)/call of duty 4 server/cstrike1.6 server and so on
I ve shared the Lvs part
I want to share this mode for gathering infomation of service on server,plz give more advice
```

* In Linux system everything is file,so we can gather every infomation from file like /proc/*/*
* Using python command output lib we can get what we want from the service.
For instance `ipvsadm -L -n --stats --exact`
* Open file and read we can get this information
* Using Popen of subprocess or os we can get the information
* Then we have to deal with these result using some mechanic like asynchronous/message queue and so on
 so let s share

## Core Code Shared

### Gathering the infomation and build the api

* Using mimimumist webframework the provide the api

When we choose the solution to make these services agent,we have so many so solution,but in python,we should make it more lighter and quicker compared with rrd/tomcat and so on
So i choose **CherryPy** to be the api entrance

* Very easy to run this server

```
if "__main__" == __name__:
    settings = {
                'global': {
                    'server.socket_port': 61777,
                    'server.socket_host': '0.0.0.0',
                    'server.socket_queue_size': 100,
                    'server.protocol_version': 'HTTP/1.1',
                    'server.log_to_screen': True,
                    'server.log_file': '/var/log/cherrypy.log',
                    'server.reverse_dns': False,
                    'server.thread_pool': 200,
                    'server.environment': 'production',
                    'engine.timeout_monitor.on': False,
                    'engine.autoreload.on': True,
                }
        }
    cherrypy.config.update(settings)
    cherrypy.tree.mount(Index(), '/')
    cherrypy.tree.mount(Node(), '/node')
    cherrypy.engine.start()
```

Then every definition interface can be expose

* Gathering every infomation using file operation

```
@cherrypy.expose
    def GetLvsStatus(self):
        Conn = []
        node_list = []
        dict = {}
        num = 0
        cmd = "ipvsadm -ln"
        lines = os.popen(cmd).readlines()
        for line in lines[3:]:
            num += 1
            con = line.split()
            if con[0] == "TCP" or con[0] == "UDP":
                if num == 1:
                    pass
                else:
                    Conn.append(dict)
                dict = {}
                dict['lb_algo'] = str(con[2])
                dict['vip'] = str(con[1])
                dict['node'] = []
                continue
            node_dict = {"rs":con[1],"lb_kind":con[2],"weight":con[3]}
            dict['node'].append(node_dict)
            if num == len(lines[3:]):
                Conn.append(dict)

        return json.dumps(Conn, sort_keys=False, indent=4, separators=(',', ': '))

    @cherrypy.expose
    def GetLvsTraffic(self):
        result = json.loads(open(os.path.join(cur_dir, 'data/', 'lvstraffic')).read())
        return json.dumps(result, sort_keys=False, indent=4, separators=(',', ': '))
```

os.popen subprocess.Popen could help us,it is more efficien then open files and read,but sometimes we have to open an fd

![](https://raw.github.com/stttt2003pk/stttt2003pk_monitor_agent_cherry/master/screenshot/cherry.png)

### Pushing stats

* Like everybody says never making wheels

I try to integrate the stats using statsd+graphite/zabbix and so on
Do not waste so much time making rrd or other wheels,world changes to fast
We should know and use these monitoring tools,thanks zabbix and statsd

[pushing stats to zabbix and using zabbix metric/graphical api we should reference these Chinesemen](https://github.com/ywzhou123/EWP_OMS)

* I try to share the most easy part using statsd

```
class AgentDaemon():
    def __init__(self):
        self.statsd_client = statsd.StatsClient(statsd_server, statsd_port, prefix=prefix)

    def push_statsd(self, k, v, type):
        if type == 'time':
            self.statsd_client.timing(k, v)
        return None

        .....


self.push_statsd('vip.%s.conns' %(_statsd_vip), vip_per_dict['conns_sum_per'], 'time')
```

![](https://raw.github.com/stttt2003pk/stttt2003pk_monitor_agent_cherry/master/screenshot/graphite.png)

### Deal with log

* To deal with log,i use fd seeker and regular expression lib
* When 're.compile' matched, make a production, let consumer do what he should do like smtp/recovery/yield and so on

![](https://raw.github.com/stttt2003pk/stttt2003pk_monitor_agent_cherry/master/screenshot/queue.png)

[reference to asynchronous using python](https://my.oschina.net/leejun2005/blog/501448)

Overwrite threading.thread 'run' method to consum this job

```
    def run(self):
        while True:
            time.sleep(1)
            if self.jobq.qsize() > 0:
                job = self.jobq.get()
                print job
                self._process_job(job)
```

![](https://raw.github.com/stttt2003pk/stttt2003pk_monitor_agent_cherry/master/screenshot/log.png)

### Dynamic problem
* Everytime non-block or queueing dealing with every job is a topic
* Rbmq zmq can help us if u have a lot time building wheels
* [Saltstack](https://saltstack.com/)/puppet/ansible(blocked)has the most available solution of agent dynamic job encap

### Socket can help us with much more flexible

* [It s an easy reference](https://github.com/stttt2003pk/stttt2003pk_game_server_manager_api/blob/master/agent.py)













