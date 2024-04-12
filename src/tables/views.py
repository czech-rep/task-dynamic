from rest_framework import views, viewsets, response, status, decorators, status

from tables.models import Table, Field
from tables.serializers import TableSerializer, dynamic_serializer_factory
from tables import table_build


class TableView(viewsets.ModelViewSet):
    http_method_names = ['post', 'put', 'get']
    queryset = Table.objects.prefetch_related('fields')
    serializer_class = TableSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def list(self, request, *args, **kwargs):
    #     return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        serializer = TableSerializer(data=request.data)

        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        table = serializer.save()
        model = table.get_model()
        table_build.create_table(model)

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        # from django.db.models.loading import cache
        # try:
        #     del cache.app_models[appname][modelname]
        # except KeyError:
        #     pass

    def update(self, request, pk, *args, **kwargs):
        try:
            table = Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TableSerializer(table, data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        model_before = table.get_model()

        serializer.save()

        table.refresh_from_db()
        model_after = table.get_model()

        table_build.alter_table(
            model=model_after,
            changes=table_build.get_model_changes(model_before, model_after),
        )

        return response.Response(serializer.data)

    @decorators.action(methods=['post'], detail=True, url_path='row')
    def add_dynamic(self, request, pk=None):
        table = self.get_object()
        model = table.get_model()

        serializer_class = dynamic_serializer_factory(model)

        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return response.Response()

    @decorators.action(methods=['get'], detail=True, url_path='rows')
    def list_dynamic(self, request, pk=None):
        table = self.get_object()
        model = table.get_model()
        serializer_class = dynamic_serializer_factory(model)

        serializer = serializer_class(model.objects.order_by('id'), many=True)
        return response.Response(serializer.data)
