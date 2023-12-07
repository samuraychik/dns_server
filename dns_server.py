from dnslib import DNSRecord
import socket


ROOT_IP = "198.41.0.4"


def request_a(domain_name, server_ip):
    request = DNSRecord.question(domain_name, qtype="A")
    response_raw = request.send(server_ip, tcp=True)
    response_parsed = DNSRecord.parse(response_raw)
    if response_parsed.rr:
        return response_parsed
    
    additional_records = response_parsed.ar
    for record in additional_records:
        if record.rtype != 1:
            continue
        return request_a(domain_name, str(record.rdata))


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(("127.0.0.1", 53))
        
        while True:
            data, addr = server.recvfrom(4096)
            query = DNSRecord.parse(data)
            query_id = query.header.id
            domain_name = query.questions[0].qname
            
            response = request_a(domain_name, ROOT_IP)
            response.header.id = query_id
            response_bytes = response.pack()
            server.sendto(response_bytes, addr)


if __name__ == "__main__":
    main()
