"""
Class for interfacing with the Censys Assets API.
"""
from typing import Optional, Generator


class Assets:
    """
    Assets API class
    """

    def __init__(self, client, asset_type):
        self.client = client
        self.base_path = f'assets/{asset_type}'

    def get_assets(
            self, page_number: Optional[int] = 1, page_size: Optional[int] = None
    ) -> Generator[dict, None, None]:
        """
        Requests assets data.

        Args:
            page_number (int, optional): Page number to begin searching for asset results.
            page_size (int, optional): Page size for retrieving assets.

        Returns:
            generator: Asset search results.
        """

        return self.client._get_page(self.base_path, page_number=page_number, page_size=page_size)

    def get_asset_by_id(self, asset_id: str) -> dict:
        """
        Requests asset data by ID.

        Args:
            asset_id (str): Requested asset ID.

        Returns:
            dict: Asset search result.
        """

        path = f'{self.base_path}/{asset_id}'

        return self.client._get(path)

    def get_comments(
            self, asset_id: str, page_number: Optional[int] = 1, page_size: Optional[int] = None
    ) -> Generator[dict, None, None]:
        """
        Requests comments on a specified asset.

        Args:
            asset_id (str): Asset ID for requested comments.
            page_number (int, optional): Page number to begin searching for comment results.
            page_size (int, optional): Page size for retrieving comments.

        Returns:
            generator: Comment search results.
        """

        path = f'{self.base_path}/{asset_id}/comments'

        return self.client._get_page(path, page_number=page_number, page_size=page_size)

    def get_comment_by_id(self, asset_id: str, comment_id: int) -> dict:
        """
        Requests a comment on a specified asset by comment ID.

        Args:
            asset_id (str): Asset ID for requested comments.
            comment_id (int): Requested comment ID.

        Returns:
            dict: Comment search result.
        """

        path = f'{self.base_path}/{asset_id}/comments/{comment_id}'

        return self.client._get(path)

    def add_comment(self, asset_id: str, comment: str) -> dict:
        """
        Adds a comment to a specified asset on the ASM platform.

        Args:
            asset_id (str): Asset ID to add comment to.
            comment (str): New comment text.

        Returns:
            dict: Added comment results.
        """

        path = f'{self.base_path}/{asset_id}/comments'
        data = {'markdown': str(comment)}

        return self.client._post(path, data=data)

    def add_tag(self, asset_id: str, name: str, color: Optional[str] = None) -> None:
        """
        Adds a tag to a specified asset on the ASM platform.

        Args:
            asset_id (str): Asset ID to add tag to.
            name (str): New tag name.
            color (str, optional): New tag color.
        """

        path = f'{self.base_path}/{asset_id}/tags'
        data = format_tag(name, color)

        return self.client._post(path, data=data)

    def delete_tag(self, asset_id: str, name: str) -> None:
        """
        Deletes a tag from a specified asset on the ASM platform by tag name.

        Args:
            asset_id (str): Asset ID to delete tag from.
            name (str): Tag name to delete.
        """

        path = f'{self.base_path}/{asset_id}/tags/{name}'

        return self.client._delete(path)


def format_tag(name: str, color: Optional[str] = None) -> dict:
    """
    Formats tag name and color request data.

    Args:
        name (str): Tag name.
        color (str, optional): Tag color.

    Returns:
            dict: Formatted tag request data.
    """

    if color:
        return {'name': str(name), 'color': str(color)}

    return {'name': str(name)}
