"""Common response formatting utilities."""
from typing import Any, Dict, Optional
from rest_framework.response import Response
from rest_framework import status as http_status


class ResponseFormatter:
    """Standardized response formatting for all endpoints."""

    @staticmethod
    def success(message: str = None, data: Any = None, status: int = http_status.HTTP_200_OK) -> Response:
        """Return a success response."""
        response_data = {"success": True}
        if message:
            response_data["message"] = message
        if data is not None:
            response_data["data"] = data
        return Response(response_data, status=status)

    @staticmethod
    def created(message: str = None, data: Any = None) -> Response:
        """Return a creation success response (201)."""
        return ResponseFormatter.success(
            message=message, data=data, status=http_status.HTTP_201_CREATED
        )

    @staticmethod
    def error(error: str, status: int = http_status.HTTP_400_BAD_REQUEST, errors: Dict = None) -> Response:
        """Return an error response."""
        response_data = {"success": False, "error": error}
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status)

    @staticmethod
    def validation_error(errors: Dict, status: int = http_status.HTTP_400_BAD_REQUEST) -> Response:
        """Return a validation error response."""
        return Response(
            {"success": False, "errors": errors},
            status=status,
        )

    @staticmethod
    def unauthorized(message: str = "Not authenticated.") -> Response:
        """Return an unauthorized response."""
        return ResponseFormatter.error(message, status=http_status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def forbidden(message: str = "Permission denied.") -> Response:
        """Return a forbidden response."""
        return ResponseFormatter.error(message, status=http_status.HTTP_403_FORBIDDEN)

    @staticmethod
    def not_found(message: str = "Resource not found.") -> Response:
        """Return a not found response."""
        return ResponseFormatter.error(message, status=http_status.HTTP_404_NOT_FOUND)

    @staticmethod
    def server_error(message: str = "An internal error occurred. Please try again later.") -> Response:
        """Return a server error response."""
        return ResponseFormatter.error(message, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaginationHelper:
    """Helper for consistent pagination responses."""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    @staticmethod
    def paginate_queryset(queryset, request, page_size: int = None):
        """Extract pagination params from request."""
        from rest_framework.pagination import PageNumberPagination

        page_size = page_size or PaginationHelper.DEFAULT_PAGE_SIZE
        page_size = min(int(request.query_params.get("page_size", page_size)), PaginationHelper.MAX_PAGE_SIZE)

        paginator = PageNumberPagination()
        paginator.page_size = page_size
        return paginator.paginate_queryset(queryset, request)

    @staticmethod
    def get_paginated_response(paginator, data: list, request=None) -> Response:
        """Format paginated response."""
        response = paginator.get_paginated_response(data)
        response.data = {
            "success": True,
            "count": response.data.get("count"),
            "next": response.data.get("next"),
            "previous": response.data.get("previous"),
            "results": response.data.get("results", []),
        }
        return response
