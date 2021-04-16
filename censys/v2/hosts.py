"""Interact with the Censys Search Host API."""
from .api import CensysSearchAPIv2


class CensysHosts(CensysSearchAPIv2):
    """Interacts with the Hosts index.

    Examples:
        Inits Censys Hosts.

        >>> from censys import CensysHosts
        >>> h = CensysHosts()

        Simple host search.

        >>> for page in h.search("service.service_name: HTTP"):
        >>>     print(page)
        [
            {
            'services':
                [
                    {'service_name': 'HTTP', 'port': 80},
                    {'service_name': 'HTTP', 'port': 443}
                ],
            'ip': '1.0.0.0'
            },
            ...
        ]

        View specific host.

        >>> h.view("1.0.0.0")
        {
            'ip': '8.8.8.8',
            'services': [{}],
            ...
        }

        Simple host aggregate.

        >>> h.aggregate("service.service_name: HTTP", "services.port", num_buckets=5)
        {
            'total_omitted': 591527370,
            'buckets': [
                {'count': 56104072, 'key': '80'},
                {'count': 43527894, 'key': '443'},
                {'count': 23070429, 'key': '7547'},
                {'count': 12970769, 'key': '30005'},
                {'count': 12825150, 'key': '22'}
            ],
            'potential_deviation': 3985101,
            'field': 'services.port',
            'query': 'service.service_name: HTTP',
            'total': 172588754
        }
    """

    INDEX_NAME = "hosts"
    """Name of Censys Index."""
