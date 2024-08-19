"""Abstract repository for working with permanent storage."""

import abc


class AbstractRepository(abc.ABC):
    """Abstract interface for working with permanent storage."""

    @abc.abstractmethod
    async def create(self, *args, **kwargs):
        """Create instance in storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, *args, **kwargs):
        """Update instance's fields."""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, *args, **kwargs):
        """Delete instance from storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, *args, **kwargs):
        """Get instance from storage by it's id, or by other attrs."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, *args, **kwargs):
        """Get list of storage instances."""
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, *args, **kwargs):
        """Save all changes to storage."""
        raise NotImplementedError
