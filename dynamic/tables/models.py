from django.db import models


class Table(models.Model):
    name = models.CharField(unique=True)

    class Meta:
        verbose_name = 'TableData'

    def compare_format(self):
        return {
            'name': self.name,
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
            'field_type': self.field_type,
            'default': self.get_default(),
        }

    def get_default(self):
        print(self.field_type)
        if self.field_type == self.FieldType.string:
            return self.default_string
        elif self.field_type == self.FieldType.number:
            return self.default_number
        elif self.field_type == self.FieldType.boolean:
            return self.default_boolean
        else:
            return None # never happens ;)
        # if self.default_number is not None:
        #     return self.default_number
        # elif self.default_string is not None:
        #     return self.default_string
        # elif self.default_boolean is not None:
        #     return self.default_boolean
        # else:
        #     return None
