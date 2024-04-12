from rest_framework import serializers

from tables.models import Table, Field


class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ['name', 'field_type', 'default_string', 'default_number', 'default_boolean']

    def to_internal_value(self, data):
        match data['field_type']:
            case Field.FieldType.string:
                data['default_string'] = data.get('default')
            case Field.FieldType.number:
                data['default_number'] = data.get('default')
            case Field.FieldType.boolean:
                data['default_boolean'] = data.get('default')
            case _:
                raise ValueError(f'not handled {data["field_type"]}')
        return super().to_internal_value(data)


class TableSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = Table
        fields = ['id', 'name', 'fields']

    def validate(self, attrs):
        if any(field['name'] == 'id' for field in attrs['fields']):
            raise serializers.ValidationError({'fields': 'forbidden name "id"'})

        if len(set(field['name'] for field in attrs['fields'])) != len(attrs['fields']):
            raise serializers.ValidationError({'fields': 'non unique field names'})
        return attrs

    def create_fields(self, table, fields_data):
        for field_data in fields_data:
            Field.objects.create(table=table, **field_data)

    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        table = Table.objects.create(**validated_data)

        self.create_fields(table, fields_data)

        return table

    def update(self, instance, validated_data):
        instance.fields.all().delete()  # we could update these objects, but its easier to delete

        fields_data = validated_data.pop('fields')
        self.create_fields(instance, fields_data)

        return super().update(instance, validated_data)


def dynamic_serializer_factory(model_):
    class Meta:
        model = model_
        fields = '__all__'

    return type(
        model_.__name__ + 'Serializer',
        (serializers.ModelSerializer, ),
        {'Meta': Meta},
    )

        # unknown =  self.initial_data.keys() - self.fields.keys()
        # if unknown:
        #     raise ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
        # return attrs