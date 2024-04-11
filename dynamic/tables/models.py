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

    class FieldType(models.IntegerChoices): # TODO to TextChoices
        string = 0, 'string'
        number = 1, 'number'
        boolen = 2, 'boolen'

    table = models.ForeignKey(to='tables.Table', on_delete=models.CASCADE, related_name='fields')
    name = models.CharField()
    field_type = models.SmallIntegerField(choices=FieldType.choices)

    class Meta:
        db_table = 'table_fields'

    def fmt(self):
        return {
            'db_column': self.name,
            'field_type': self.field_type,
        }
