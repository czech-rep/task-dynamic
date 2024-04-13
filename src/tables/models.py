from django.db import models


class Table(models.Model):

    @property
    def name(self):
        return 'dynamic_table_' + str(self.id).zfill(3)

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

    default = models.CharField(null=True)

    class Meta:
        pass
        # TODO unique together: field name and table. For now, its validated in serializer

    def get_default(self):
        if self.default is None:  # fiels has no default value
            return None
        elif self.field_type == self.FieldType.string:
            return self.default
        elif self.field_type == self.FieldType.number:
            return int(self.default)
        elif self.field_type == self.FieldType.boolean:
            return bool(self.default)
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
