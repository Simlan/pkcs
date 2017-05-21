#!/usr/bin/env python
# coding=utf8

import sys
import argparse
import os
from os.path import expanduser
import subprocess
import logging
import opensslconf

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

GEN_CA_KEY = 'openssl genrsa -out  %(caroot)s/%(cn)s-key.pem %(key_len)s'
GEN_CA_REQ = 'openssl req -new -key %(caroot)s/%(cn)s-key.pem -config %(caroot)s/openssl.conf -subj "%(subj)s" -batch -out %(caroot)s/%(cn)s-csr.pem'
GEN_CA_CERT = 'openssl ca -config %(caroot)s/openssl.conf -create_serial -out %(caroot)s/%(cn)s.cer -days 365 -keyfile %(caroot)s/%(cn)s-key.pem -selfsign -in %(caroot)s/%(cn)s-csr.pem -batch'

GEN_CERT_KEY = 'openssl genrsa -out %(cn)s_key.pem %(key_len)s'
GEN_CERT_REQ = 'openssl req -new -key    web_key.pem -passin pass:Yunweipai@123 -config /home/yunweipai/openssl_ca/openssl.conf -subj "/C=CN/ST=GuangDong/L=ShenZhen/O=UProject/OU=Yunweipai/CN=www.yunweipai.com" -batch -out   web_csr.pem'
GEN_CERT = 'openssl ca -days 365 -config openssl.conf -keyfile ca_key.pem -key Yunweipai@123 -cert ca_cert.cer -in /home/yunweipai/user_certs/web_csr.pem -out web.cer'

class CA(object):
    def __init__(self, argsv):
        self.caroot = os.path.join(os.path.join(expanduser("~"), 'pkcs'), 'ca')
        self.argsv = argsv
        self.parser = argparse.ArgumentParser(prog='pkcs ca', description='pkcs tool set')
        self.parser.add_argument('-root', '--ca-root', dest='caroot', default=self.caroot, help="ca output path")
        self.parser.add_argument('-len', '--key-len', dest='len', default=4096, help="ca key length")
        self.parser.add_argument('-c', '--country', dest='c', default='CN', help="country name in subject")
        self.parser.add_argument('-st', '--state', dest='st', default='GuangDong', help="state or province name in subject")
        self.parser.add_argument('-l', '--locality', dest='l', default='ShenZhen', help="locality name in subject")
        self.parser.add_argument('-o', '--organization', dest='o', default='YunWeiPai', help="organization name in subject")
        self.parser.add_argument('-ou', '--organization-unit', dest='ou', default='YunWeiPai', help="organization unit name in subject")
        self.parser.add_argument('-cn', '--common-name', dest='cn', default='YunWeiPai-CA', help="common name in subject")
        self.args = None

    def parse(self):
        self.args = self.parser.parse_args(self.argsv)
        self.caroot = self.args.caroot
        self.len = self.args.len
        self.c = self.args.c
        self.st = self.args.st
        self.l = self.args.l
        self.o = self.args.o
        self.ou = self.args.ou
        self.cn = self.args.cn
        self.subject = "/C=%(c)s/ST=%(st)s/L=%(l)s/O=%(o)s/OU=%(ou)s/CN=%(cn)s" % {
            "c": self.c,
            "st": self.st,
            "l": self.l,
            "o": self.o,
            "ou": self.ou,
            "cn": self.cn,
            "caroot": self.caroot
        }
        return True

    def execute(self):
        logging.info("start generate CA ...")
        if not os.path.isdir(self.caroot):
            logging.info("make dir %s", self.caroot)
            os.makedirs(self.caroot)

        logging.info('setup openssl.conf file')
        self._setupOpensslConfFile()

        if not os.path.isdir(os.path.join(self.caroot, 'certsdb')):
            logging.info('setup ca environment')
            os.makedirs(os.path.join(self.caroot, 'certsdb'))
        indexFile = os.path.join(self.caroot, 'index.txt')
        if not os.path.isfile(indexFile):
            with open(indexFile, 'w+'):
                os.utime(indexFile, None)

        cmd = GEN_CA_KEY % {'key_len': self.len, 'caroot': self.caroot, "cn": self.cn}
        logging.info('generate ca key by command: %s', cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        if p.returncode != 0:
            logging.error("generate ca key failure")
            return p.returncode

        cmd = GEN_CA_REQ % {'caroot': self.caroot, 'subj': self.subject, "cn": self.cn}
        logging.info('generate ca certificate request by command: %s', cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        if p.returncode != 0:
            logging.error("generate ca certificate request failure")
            return p.returncode
        
        cmd = GEN_CA_CERT % {'caroot': self.caroot, "cn": self.cn}
        logging.info('generate ca certificate by command: %s', cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        if p.returncode != 0:
            logging.error("generate ca certificate failure")
            return p.returncode
        return 0

    def usage(self):
        self.parser.print_help()

    def _setupOpensslConfFile(self):
        conf = opensslconf.opensslConf % {
            "c": self.c,
            "st": self.st,
            "l": self.l,
            "o": self.o,
            "ou": self.ou,
            "cn": self.cn,
            "caroot": self.caroot
        }
        confFile = os.path.join(self.caroot, 'openssl.conf')
        with open(confFile, 'w+') as fp:
            fp.write(conf)


class Cert(object):
    def __init__(self, argsv):
        self.curPath = os.path.dirname(os.path.realpath(__file__))
        self.defaultOut = os.path.join(expanduser("~"), 'pkcs')
        self.argsv = argsv
        self.parser = argparse.ArgumentParser(prog='pkcs cert', description='pkcs tool set')
        self.parser.add_argument('-o', '--out', dest='caroot', default=self.defaultOut, help="cert output path")
        self.parser.add_argument('-len', '--key-len', dest='len', default=4096, help="ca key length")
        self.parser.add_argument('-subj', '--subject', dest='subj', default=CA_SUBJECT, help="ca subject")
        self.args = None

    def parse(self):
        pass

    def execute(self):
        pass

    def usage(self):
        pass

def usage():
    print "%s <ca|cert> [options]" % sys.argv[0]

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    subCommand = sys.argv[1]
    cmd = None
    if subCommand == "ca":
        cmd = CA(sys.argv[2:])
        print sys.argv[2:]
    elif subCommand == "cert":
        cmd = Cert(sys.argv[1:])
    else:
        usage()
        sys.exit(1)
    if not cmd.parse():
        cmd.usage()
        sys.exit(1)
    exitcode = cmd.execute()
    sys.exit(exitcode)

