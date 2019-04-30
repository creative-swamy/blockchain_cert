"""
Verify blockchain certificates (http://www.blockcerts.org/)

Overview of verification steps
- Check integrity: TODO: json-ld normalizatio
- Check signature (pre-v2)
- Check whether revoked
- Check whether expired
- Check authenticity

"""
import json

from cert_core import to_certificate_model
from cert_verifier import connectors
from cert_verifier.checks import create_verification_steps
import sys
import binascii
import subprocess

def verify_certificate(certificate_model, options={}):
    # lookup issuer-hosted information
    issuer_info = connectors.get_issuer_info(certificate_model)

    # lookup transaction information
    connector = connectors.createTransactionLookupConnector(certificate_model.chain, options)
    transaction_info = connector.lookup_tx(certificate_model.txid)
    # create verification plan
    verification_steps = create_verification_steps(certificate_model, transaction_info, issuer_info,
                                                   certificate_model.chain)
    verification_steps.execute()
    messages = []
    verification_steps.add_detailed_status(messages)
    for message in messages:
        print(message['name'] + ',' + str(message['status']))

    return messages

def get_merklehash_from_ipfs(hexa_ipfs_link):
    asci_ipfs_link = binascii.unhexlify(hexa_ipfs_link)
    asci_ipfs_link = str(asci_ipfs_link, 'ascii')
    command = "ipfs "+"cat "+asci_ipfs_link
    output = subprocess.check_output(command, shell=True)
    actual_merkle_root = str(output, 'ascii')
    actual_merkle_root = actual_merkle_root[:-1]
    print("Actual merkle root ", actual_merkle_root)
    return actual_merkle_root

def verify_certificate_file(certificate_file_name, transaction_id=None, options={}):
    with open(certificate_file_name, 'rb') as cert_fp:
        certificate_bytes = cert_fp.read()
        certificate_json = json.loads(certificate_bytes.decode('utf-8'))
        certificate_json["signature"]["merkleRoot"]=  get_merklehash_from_ipfs(certificate_json["signature"]["merkleRoot"])
        certificate_model = to_certificate_model(certificate_json=certificate_json,
                                                       txid=transaction_id,
                                                       certificate_bytes=certificate_bytes)
        print(certificate_json)
        result = verify_certificate(certificate_model, options)
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for cert_file in sys.argv[1:]:
            print(cert_file)
            result = verify_certificate_file(cert_file)
            print(result)
    else:
        result = verify_certificate_file('../tests/data/2.0/valid.json')
        print(result)
