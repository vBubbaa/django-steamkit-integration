from rest_framework import pagination, response


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return response.Response({
            'pagination': {
                'total': self.page.paginator.count,
                'num_pages': self.page.paginator.num_pages,
                'current_page': self.request.query_params.get('page', None),
                'next_page_url': self.get_next_link(),
                'previous_page_url': self.get_previous_link(),
            },
            'data': data
        })
