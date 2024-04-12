from django.db import models


class Table(models.Model):
    class Meta:
        pass

    @property
    def name(self):
        return 'dynamic_table_' + str(self.id).zfill(3)

    def compare_format(self):
        return {
            'fields': {field.name: field.fmt() for field in self.fields.all()},
        }

class Field(models.Model):

    class FieldType(models.TextChoices): # TODO to TextChoices
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
        db_table = 'table_fields'
        # TODO unique together: field name and table

    def fmt(self):
        return {
            'db_column': self.name,
            'name': self.name,
            'field_type': self.field_type,
            'default': self.get_default(),
        }

    def get_default(self):
        """If this returns None, it means that fiels will be mandatory"""
        if self.field_type == self.FieldType.string:
            return self.default_string
        elif self.field_type == self.FieldType.number:
            return self.default_number
        elif self.field_type == self.FieldType.boolean:
            return self.default_boolean
        else:
            raise ValueError(f'unhandled {self.field_type}')
