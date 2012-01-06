#!/usr/bin/env python
"""
Cat AMQP exchange

"""
from optparse import OptionParser

import amqplib.client_0_8 as amqp
import json
import sys

VERSION = '0.0.1'

log=sys.stdout

def callback(msg):
    print "[%s:%s]" % (msg.delivery_info['routing_key'], msg.delivery_info['delivery_tag'])
    for key, val in msg.properties.items():
        log.write('%s: %s\n' % (str(key), str(val)))
    for key, val in msg.delivery_info.items():
        log.write('> %s: %s\n' % (str(key), str(val)))
    try:
        body=json.dumps(json.loads(msg.body), sort_keys=True, indent=4)
    except:
        body=str(msg.body)
    log.write("msg: " + body + '\n')
    log.write('-------\n')
    msg.channel.basic_ack(msg.delivery_tag)

def main():
    parser = OptionParser(usage="usage: %prog [options] exchange",
        version="%prog " + VERSION)
    parser = OptionParser()
    parser.add_option('--host', dest='host', default='localhost',
            help='AMQP server to connect to (default: %default)')
    parser.add_option('--port', dest='port', default=5672,
            help='AMQP server\' port to connect to (default: %default)')
    parser.add_option('--ssl', dest='ssl', action='store_true', default=False,
            help='Use ssl(default: %default)')
    parser.add_option('-u', '--user', '--userid', dest='userid', default='guest',
            help='userid to authenticate as (default: %default)')
    parser.add_option('-p', '--password', dest='password', default='guest',
            help='password to authenticate with (default: %default)')
    parser.add_option('--virtual-host', dest='virtual_host', default='/',
            help='Virtual hostname (default: %default)')
    parser.add_option('-k', '--routing_key', dest='routing_key', default='#',
            help='Routing key (default: %default)')
    parser.add_option('-t', '--trace', dest='trace', action="store_true", default=False,
            help='Trace mode (listen amq.rabbitmq.trace, write output to "trace.log")')
    parser.add_option('-f', '--file', dest='file', default='',
            help='Write output to specified file')
    (options, args) = parser.parse_args()

    if options.trace:
        options.file = options.file if options.file else 'trace.log'
        exchange='amq.rabbitmq.trace'
    else:
        exchange=args[0]
    if options.file and options.file != '-':
        global log
        log=open(options.file,"w",0)

    conn = amqp.Connection(options.host, port=options.port, userid=options.userid, password=options.password, ssl=options.ssl)

    ch = conn.channel()
    qname, _, _ = ch.queue_declare()
    ch.queue_bind(qname, exchange, routing_key=options.routing_key)
    ch.basic_consume(qname, callback=callback)

    #
    # Loop as long as the channel has callbacks registered
    #
    while ch.callbacks:
        ch.wait()

    ch.close()
    conn.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

