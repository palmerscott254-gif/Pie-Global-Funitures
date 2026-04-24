"""Shared file cleanup helpers used by model signal handlers."""


def delete_field_file(field):
    """
    Delete a file field safely without breaking the request lifecycle.

    Works with Django FieldFile objects and avoids errors if the storage
    backend or file no longer exists.
    """
    try:
        if field and getattr(field, 'name', None):
            storage = field.storage
            name = field.name
            field.delete(save=False)
            if storage.exists(name):
                storage.delete(name)
    except Exception:
        pass
