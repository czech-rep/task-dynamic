from rest_framework import views, viewsets, response, status, decorators

from tables.models import Table, Field
from tables.serializers import TableSerializer, dynamic_serializer_factory
from tables import table_build


# class RoomViewset(viewsets.ModelViewSet):
#     http_method_names = ['post', 'put', 'get']
#     serializer_class = TableSerializer


    # def create(self):
    #     pass
    # def get_serializer_class(self):
    #     if self.request.method in ['post', 'put']:
    #         return table_serializers.CreateTableSerializer
    #     else:
    #         return table_serializers.TableSerializer

class TableView(viewsets.ModelViewSet):
    queryset = Table.objects.prefetch_related('fields')
    serializer_class = TableSerializer

    def create(self, request, *args, **kwargs):
        serializer = TableSerializer(data=request.data)

        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        table = serializer.save()
        model = table_build.get_model(table)
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

        model_before = table_build.get_model(table)

        serializer.save()

        table.refresh_from_db()
        model_after = table_build.get_model(table)

        models_fields = lambda model: {field.name: field for field in model._meta.fields}

        changes=list(table_build.get_changes(models_fields(model_before), models_fields(model_after)))
        print(changes)

        table_build.alter_table(
            model=model_after,
            # model=table_build.get_model(table),
            changes=changes,
        )

        return response.Response(serializer.data)

    @decorators.action(methods=['post'], detail=True, url_path='row')
    def add_dynamic(self, request, pk=None):
        model = table_build.get_model(self.get_object())
        serializer_class = dynamic_serializer_factory(model)

        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return response.Response()

    @decorators.action(methods=['get'], detail=True, url_path='rows')
    def fetch_dynamic(self, request, pk=None):
        model = table_build.get_model(self.get_object())
        serializer_class = dynamic_serializer_factory(model)

        serializer = serializer_class(model.objects.all(), many=True)
        return response.Response(serializer.data)
