"""List all domains and subdomains in ASM."""

from censys.asm import DomainsAssets

d = DomainsAssets()

domains = []
for domain in d.get_assets():
    domain_str = domain["data"]["domain"]
    domains.append(domain_str)
    subdomains = [sub["subdomain"] for sub in d.get_subdomains(domain_str)]
    domains.extend(subdomains)

print(domains)
