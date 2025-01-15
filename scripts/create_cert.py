import trustme
from pathlib import Path
from argparse import ArgumentParser


def main(ca_name: str, server: str):
    ca = trustme.CA(
        organization_name=ca_name, organization_unit_name="HTCondor Dashboard"
    )
    server_cert = ca.issue_cert(server)

    tmp_dir = Path("/tmp") / server
    tmp_dir.mkdir(exist_ok=True)

    key = Path(tmp_dir) / "hostkey.pem"
    server_cert.private_key_pem.write_to_path(key)

    cert = Path(tmp_dir) / "hostcert.pem"
    server_cert.cert_chain_pems[-1].write_to_path(cert)

    ca_cert = Path(tmp_dir) / f"{ca_name}.pem"
    ca.cert_pem.write_to_path(ca_cert)

    print(f"Key: {key}")
    print(f"Cert: {cert}")
    print(f"CA Cert: {ca_cert}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--ca-name",
        type=str,
        required=True,
        help="Common Name for the Certificate Authority",
    )
    parser.add_argument(
        "--server",
        type=str,
        required=True,
        help="Common Name for the server certificate",
    )
    args = parser.parse_args()

    main(args.ca_name, args.server)
