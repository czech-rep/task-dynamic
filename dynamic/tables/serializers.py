from rest_framework import serializers

from tables.models import Table, Field


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ['name', 'field_type']


# class SimpleTable(serializers.ModelSerializer):
#     class Meta:
#         model = Table
#         fields = '__all__'


class TableSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = Table
        fields = ['name', 'fields']

    def validate(self, attrs):
        if len(set(field['name'] for field in attrs['fields'])) != len(attrs['fields']):
            raise serializers.ValidationError({'fields': 'non unique field names'})
        return attrs

    def create_fields(self, table, fields_data):
        for field_data in fields_data:
            Field.objects.create(table=table, **field_data)

    def create(self, validated_data):
        print('create---')
        fields_data = validated_data.pop('fields')
        table = Table.objects.create(**validated_data)

        self.create_fields(table, fields_data)

        return table

    def update(self, instance, validated_data):
        # we could update these objects, but uts easier to
        # instance.objects.delete()
        instance.fields.all().delete()

        fields_data = validated_data.pop('fields')
        self.create_fields(instance, fields_data)

        return super().update(instance, validated_data)




# what with update?