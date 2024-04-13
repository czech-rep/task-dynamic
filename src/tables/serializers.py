from collections import Counter
from rest_framework import serializers

from tables.models import Table, Field


class UniversalField(serializers.Field):
    def to_representation(self, data):
        return str(data)

    def to_internal_value(self, data):
        return str(data)


class FieldSerializer(serializers.ModelSerializer):
    default = UniversalField(required=False)

    class Meta:
        model = Field
        fields = ['name', 'field_type', 'default']

    def validate(self, attrs):
        default = attrs.get('default')

        if default is None:
            return attrs

        match attrs['field_type']:
            case Field.FieldType.string:
                pass

            case Field.FieldType.number:
                if not default.isnumeric():
                    raise serializers.ValidationError({'default': 'invalid number'})

            case Field.FieldType.boolean:
                if not default.lower() in ['true', 'false']:
                    raise serializers.ValidationError({'default': 'invalid boolean'})

            case _:
                raise serializers.ValidationError({'field_type': 'invalid field_type'})

        return attrs


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

        if instanc  e := getattr(self, 'instance'):
            incoming_field_by_name = {field['name']: field for field in attrs['fields']}

            for field in instance.fields.all():
                if (
                    field.name in incoming_field_by_name
                    and field.field_type != incoming_field_by_name[field.name]['field_type']
                ):
                    raise serializers.ValidationError({'fields': f'change of field type forbidden: {field.name}'})

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
