from django.db import models


class Table(models.Model):

    @property
    def name(self):
        return 'dynamic_table_' + str(self.id).zfill(3)

    def compare_format(self):
        return {
            'fields': {field.name: field.fmt() for field in self.fields.all()},
        }

    def get_model(self):
        attrs = {field.name: field.as_field_instance() for field in self.fields.all()}

        attrs['__module__'] = 'tables.models'

        model = type(
            self.name,
            (models.Model, ),
            attrs,
        )

        model._meta.db_table = self.name

        return model

class Field(models.Model):

    class FieldType(models.TextChoices):
        string = 'string'
        number = 'number'
        boolean = 'boolean'

    table = models.ForeignKey(to='tables.Table', on_delete=models.CASCADE, related_name='fields')
    name = models.CharField()
    field_type = models.CharField(choices=FieldType.choices)

    default_number = models.IntegerField(null=True)
    default_string = models.CharField(null=True)
    default_boolean = models.BooleanField(null=True)

    class Meta:
        pass
        # TODO unique together: field name and table. For now, its validated in serializer

    def get_default(self):
        """If this returns None, it means that fiels has no default value"""
        if self.field_type == self.FieldType.string:
            return self.default_string
        elif self.field_type == self.FieldType.number:
            return self.default_number
        elif self.field_type == self.FieldType.boolean:
            return self.default_boolean
        else:
            raise ValueError(f'unhandled {self.field_type}')

    def attrs(self):
        result = {
            'db_column': self.name,
            'name': self.name,
        }
        if self.get_default() is None:
            result['null'] = True
        else:
            result['default'] = self.get_default()
            result['null'] = False

        return result

    def as_field_instance(self):
        match self.field_type:
            case Field.FieldType.string:
                field = models.CharField(**self.attrs())
            case Field.FieldType.number:
                field = models.IntegerField(**self.attrs())
            case Field.FieldType.boolean:
                field = models.BooleanField(**self.attrs())
            case _:
                raise ValueError(f'{self.field_type} not handled')

        field.column = field.db_column
        return field
