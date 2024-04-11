from rest_framework import views, viewsets, response, status

from tables.models import Table, Field
from tables.serializers import TableSerializer
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

        return response.Response(status=status.HTTP_201_CREATED)

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

        table_before = table.compare_format()

        serializer.save()

        table.refresh_from_db()
        table_after = table.compare_format()

        changes=list(table_build.get_changes(table_before, table_after))
        print(changes)

        table_build.alter_table(
            model=table_build.get_model(table),
            changes=changes,
        )

        return response.Response(serializer.data)
