#! /usr/bin/env python

"""
Certificate authorit stuffs
"""

import os

from M2Crypto import RSA, X509, EVP, m2

class CertificateAuthority(object):

    def __init__(self, path='tmp', passphrase="secret"):
        self.path = path
        self.privpath = os.path.join(path, 'key.pem')

        try:
            rsa = RSA.load_key(self.privpath, passphrase)
        except IOError:
            rsa = generateRSAKey(self.privpath)

        self.publicKey = generatePublicKey(rsa)

        self.pubpath = os.path.join(path, 'pub.pem')

        try:
            self.cert = X509.load_cert(self.pubpath)
        except IOError:
            req = makeRequest(self.publicKey)
            self.cert = makeCert(req, self.publicKey)
            self.cert.sign(self.publicKey, 'sha1')
            f = open(self.pubpath, 'w')
            f.write(self.cert.as_text())
            f.write(self.cert.as_pem())
            f.close()

    def generate_signed(self):
        rsa = generateRSAKey('tmp/k1.pem')
        publicKey = generatePublicKey(rsa)
        req = makeRequest(publicKey)
        cert = makeCert(req, self.publicKey)
        cert.save('tmp/c1.pem', 1)

        print cert.check_ca()

        f = open('tmp/s.pem', 'w')
        f.write(open('tmp/k1.pem').read())
        f.write(cert.as_text())
        f.write(open('tmp/c1.pem').read())
        f.close()

def generateRSAKey(privpath):
    rsa = RSA.gen_key(2048, m2.RSA_F4)
    rsa.save_key(privpath, cipher='aes_256_cbc', callback=passphrase)
    return rsa

def generatePublicKey(key):
    publicKey = EVP.PKey()
    publicKey.assign_rsa(key)
    return publicKey

def makeRequest(publicKey):
    req = X509.Request()
    req.set_version(2)
    req.set_pubkey(publicKey)
    name = X509.X509_Name()
    name.CN = 'My CA, Inc.'
    req.set_subject_name(name)
    ext1 = X509.new_extension('subjectAltName', 'DNS:foobar.example.com')
    ext2 = X509.new_extension('nsComment', 'Hello there')
    extstack = X509.X509_Extension_Stack()
    extstack.push(ext1)
    extstack.push(ext2)

    assert(extstack[1].get_name() == 'nsComment')
    
    req.add_extensions(extstack)
    req.sign(publicKey, 'sha1')
    return req

def makeCert(req, caPkey):
    publicKey = req.get_pubkey()
    #woop = generatePublicKey(generateRSAKey())
    #if not req.verify(woop.publicKey):
    if not req.verify(publicKey):
        # XXX What error object should I use?
        raise ValueError, 'Error verifying request'
    sub = req.get_subject()
    # If this were a real certificate request, you would display
# all the relevant data from the request and ask a human operator
    # if you were sure. Now we just create the certificate blindly based
    # on the request.
    cert = X509.X509()
    # We know we are making CA cert now...
    # Serial defaults to 0.
    cert.set_serial_number(1)
    cert.set_version(2)
    cert.set_subject(sub)
    issuer = X509.X509_Name()
    issuer.CN = 'The Issuer Monkey'
    issuer.O = 'The Organization Otherwise Known as My CA, Inc.'
    cert.set_issuer(issuer)
    cert.set_pubkey(publicKey)
    notBefore = m2.x509_get_not_before(cert.x509)
    notAfter  = m2.x509_get_not_after(cert.x509)
    m2.x509_gmtime_adj(notBefore, 0)
    days = 30
    m2.x509_gmtime_adj(notAfter, 60*60*24*days)
    cert.add_ext(
        X509.new_extension('subjectAltName', 'DNS:foobar.example.com'))
    ext = X509.new_extension('nsComment', 'M2Crypto generated certificate')
    ext.set_critical(0)# Defaults to non-critical, but we can also set it
    cert.add_ext(ext)
    cert.sign(caPkey, 'sha1')

    assert(cert.get_ext('subjectAltName').get_name() == 'subjectAltName')
    assert(cert.get_ext_at(0).get_name() == 'subjectAltName')
    assert(cert.get_ext_at(0).get_value() == 'DNS:foobar.example.com')
    
    return cert

if __name__ == '__main__':
    ca = CertificateAuthority()
    ca.generate_signed()
