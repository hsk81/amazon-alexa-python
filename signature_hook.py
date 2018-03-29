__author__ = 'hsk81'

###########################################################################
###########################################################################

from OpenSSL import crypto

import base64
import falcon
import logging
import os
import os.path
import pem
import re
import requests
import urllib.parse

###########################################################################
###########################################################################

class SignatureHook(object):

    def __call__(self, req, res, *args, **kwargs):

        scc_url = self.certificate_url(req=req)
        assert scc_url is not None
        url_chk = self.verify_url(scc_url)
        assert url_chk is not None
        scc_pem = self.cached_pem(scc_url)
        assert scc_pem is not None

        ca_cert = self.verify_pem(scc_pem, req=req)
        assert ca_cert is not None
        req_sig = self.verify_sig(ca_cert, req=req)
        assert req_sig is not None

    def certificate_url(self, req):

        certificate_url = req.get_header('SignatureCertChainUrl')
        if not certificate_url or certificate_url == '':
            raise falcon.HTTPBadRequest(
                description='no certificate URL header', headers={
                    'SignatureCertChainUrl': certificate_url
                })

        return certificate_url

    def signature(self, req):

        signature = req.get_header('Signature')
        if not signature or signature == '':
            raise falcon.HTTPBadRequest(
                description='no signature header', headers={
                    'Signature': signature
                })

        return signature

    def verify_url(self, url):

        uri = urllib.parse.urlparse(url)
        assert uri.scheme is not None
        assert uri.netloc is not None
        assert uri.path is not None

        if not URI.local(uri) \
           and uri.scheme not in ['https']:

            raise falcon.HTTPBadRequest(
                description='invalid protocol for URL', headers={
                    'SignatureCertChainUrl': url
                })

        if not URI.local(uri) \
           and uri.netloc not in [
            's3.amazonaws.com', 's3.amazonaws.com:443']:

            raise falcon.HTTPBadRequest(
                description='invalid netloc for URL', headers={
                    'SignatureCertChainUrl': url
                })

        if not uri.path.startswith('/echo.api'):

            raise falcon.HTTPBadRequest(
                description='invalid path for URL', headers={
                    'SignatureCertChainUrl': url
                })

        return True

    def cached_pem(self, url):

        if not rdb.connection.exists(url):

            uri = urllib.parse.urlparse(url)
            if URI.local(uri):
                with open('./static' + uri.path) as file:
                    rdb.connection.set(url, file.read())
            else:
                res = requests.get(url)
                if res.status_code != 200:
                    raise falcon.HTTPBadRequest(
                        description='invalid status for URL',
                        headers={'SignatureCertChainUrl': url})

                rdb.connection.set(url, res.text)

        cached_pem = rdb.connection.get(url) ## certificate-chain.pem
        assert cached_pem and cached_pem != ''
        return cached_pem

    def verify_pem(self, pem_text, req, ca_store=None):

        if ca_store is None:
            ca_store = self.ca_store()

        ca_certs, certs = [], pem.parse(pem_text)
        for i, cert in enumerate(certs):
            ca_certs.append(crypto.load_certificate(
                crypto.FILETYPE_PEM, cert.as_bytes()))

            try:
                crypto.X509StoreContext(ca_store, ca_certs[i]) \
                      .verify_certificate()

            except crypto.X509StoreContextError as ex:
                logging.error('issuer:{} and subject:{}'.format(
                    ca_certs[i].get_subject(), ca_certs[i].get_issuer()
                ))
                logging.error(ex)
                ca_certs.pop()
                break

        if len(ca_certs) != len(certs):
            raise falcon.HTTPBadRequest(
                description='certificate verification failed', headers={
                    'SignatureCertChainUrl': self.certificate_url(req),
                    'Signature': self.signature(req)
                })
        else:
            return ca_certs[0]

    def verify_sig(self, ca_cert, req):

        signature = self.signature(req)
        assert signature is not None
        signature_bin = base64.b64decode(signature)
        assert signature_bin is not None

        try:
            crypto.verify(ca_cert, signature_bin, req.body, 'sha1')

        except crypto.Error as ex:
            logging.error(ex)

            raise falcon.HTTPBadRequest(
                description='signature verification failed', headers={
                    'SignatureCertChainUrl': self.certificate_url(req),
                    'Signature': signature
                })

        return signature

    @classmethod
    def ca_store(cls):

        crt_paths = os.environ.get('CRT_PATH', '/etc/ssl')
        crt_flush = os.environ.get('CRT_FLUSH')

        if hasattr(cls, 'store') and not crt_flush:
            return cls.store

        else:
            cls.store = crypto.X509Store()
            suffix = r'(.+)\.(crt|pem)$'

            for crt_path in crt_paths.split(':'):
                for root, ds, fs in os.walk(crt_path):
                    for p in filter(lambda f: re.match(suffix, f), fs):
                        for cert in pem.parse_file(os.path.join(root, p)):

                            try:
                                cls.store.add_cert(
                                    crypto.load_certificate(
                                        crypto.FILETYPE_PEM,
                                        cert.as_bytes()))

                            except crypto.Error:
                                pass

            return cls.store

###########################################################################

class URI(object):

    @staticmethod
    def local(uri):
        return uri.netloc.split(':')[0] in ['localhost', '127.0.0.1']

###########################################################################
###########################################################################

import redis

class RDB(object):

    def __init__(self, url, db='0'):

        self.connection = redis.StrictRedis.from_url(url, db=db)

rdb = RDB(url='redis://localhost:6379')

###########################################################################
###########################################################################

