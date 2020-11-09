"""
Class for interfacing with the Censys Seeds API.
"""
from typing import Optional


class Seeds:
    """
    Seeds API class
    """

    def __init__(self, client):
        self.client = client
        self.base_path = "seeds"

    def get_seeds(self, seed_type: Optional[str] = None) -> dict:
        """
        Requests seed data.

        Args:
            seed_type (str, optional): Seed type ['IP_ADDRESS', 'DOMAIN_NAME', 'CIDR', 'ASN'].

        Returns:
            dict: Seed search results.
        """

        args = {"type": seed_type}

        return self.client._get(self.base_path, args=args)["seeds"]

    def get_seed_by_id(self, seed_id: int) -> dict:
        """
        Requests seed data by ID.

        Args:
            seed_id (int): Seed ID to get.

        Returns:
            dict: Seed search result.
        """

        path = f"{self.base_path}/{seed_id}"

        return self.client._get(path)

    def add_seeds(self, seeds: list, force: Optional[bool] = False) -> dict:
        """
        Add seeds to the ASM platform.

        Args:
            seeds (list): List of seed objects to add.
            force (bool, optional): Determines if add operation should be forced or not.

        Returns:
            dict: Added seeds results.
        """

        data = {"seeds": seeds}
        args = {"force": force}

        return self.client._post(self.base_path, args=args, data=data)

    def replace_seeds_by_label(
        self, label: str, seeds: list, force: Optional[bool] = False
    ) -> dict:
        """
        Replace seeds in the ASM platform by label.

        Args:
            label (str): Label name to replace by.
            seeds (list): List of seed objects to add.
            force (bool, optional): Determines if replace operation should be forced or not.

        Returns:
            dict: Added and removed seeds results.
        """

        data = {"seeds": seeds}
        args = {"label": label, "force": force}

        return self.client._put(self.base_path, args=args, data=data)

    def delete_seeds_by_label(self, label: str) -> None:
        """
        Delete seeds in the ASM platform by label.

        Args:
            label (str): Label name to delete by.
        """

        args = {"label": label}

        return self.client._delete(self.base_path, args=args)

    def delete_seed_by_id(self, seed_id: int) -> None:
        """
        Delete a seed in the ASM platform by id.

        Args:
            seed_id (int): Seed ID to delete by.
        """

        path = f"{self.base_path}/{seed_id}"

        return self.client._delete(path)
