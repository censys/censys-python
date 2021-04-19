"""List all domains and subdomains in ASM."""
from censys import AsmClient

c = AsmClient()

domains = []
for domain in c.domains.get_assets():
    domain_str = domain["data"]["domain"]
    domains.append(domain_str)
    subdomains = [sub["subdomain"] for sub in c.domains.get_subdomains(domain_str)]
    domains.extend(subdomains)

print(domains)
