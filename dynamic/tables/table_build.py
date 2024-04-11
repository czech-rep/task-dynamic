from django.db import models, connection

from tables.models import Table, Field


# provided Table instance with its Fields
# we need to assemble Model class and then create and migrate it

def field_instance(field_attrs: dict):
    """based on fmt() dict"""

    if 'default' not in field_attrs:
        field_attrs['null'] = True

    match field_attrs.pop('field_type'):
        case Field.FieldType.string:
            field = models.CharField(**field_attrs)
        case Field.FieldType.number:
            field = models.IntegerField(**field_attrs)
        case Field.FieldType.boolen:
            field = models.BooleanField(**field_attrs)

    field.column = field.db_column
    return field


def custom_table_name(name):
    return f'dynamic_table_{name}'


def get_model(table):
    attrs = {field.name: field_instance(field.fmt()) for field in table.fields.all()}

    # class Meta:
    #     abstract = False
    #     db_table = custom_table_name(table.name)

    # attrs['_meta'] = Meta
    attrs['__module__'] = 'tables.models'

    model = type(
        custom_table_name(table.name),
        (models.Model, ),
        attrs,
    )

    model._meta.db_table = custom_table_name(table.name)

    return model


def get_changes(m1, m2):
    # args: dictionaries in "compare format"
    # functimodel_buildon to compare exising Table model with new option provided
    # it would detect allowed operations like:
    # - change table name # alter_db_table(model, old_db_table, new_db_table)
    # - add field - it will be not required (compare with .fields)
    # - remove field - if its missing
    # - change field type - This includes changing the name of the column (the db_column attribute), changing the type of the field (if the field class changes),
    # - change of field name is impossible
    if m1['name'] != m2['name']:
        yield 'alter_db_table', custom_table_name(m1['name']), custom_table_name(m2['name']) # here real names
        # alter_db_table_comment(model, old_db_table_comment, new_db_table_comment)

    for new_field in m2['fields'].keys() - m1['fields'].keys():
        field_data = m2['fields'][new_field]
        yield 'add_field', field_instance(field_data)

    for removed_field in m1['fields'].keys() - m2['fields'].keys():
        field_data = m1['fields'][removed_field]
        yield 'remove_field', field_instance(field_data)

    for common_field in m1['fields'].keys() & m2['fields'].keys():
        field_old = m1['fields'][common_field]
        field_new = m2['fields'][common_field]
        if field_old != field_new:
            yield 'alter_field', field_instance(field_old), field_instance(field_new)


def alter_table(model ,changes):
    with connection.schema_editor() as editor:
        for change, *args in changes:
            match change:
                case 'alter_db_table':
                    editor.alter_db_table(model, *args)
                case 'add_field':
                    editor.add_field(model, *args)
                case 'remove_field':
                    editor.remove_field(model, *args)


def create_table(model):
    with connection.schema_editor() as editor:
        editor.create_model(model)


def remove_table(model):
    with connection.schema_editor() as editor:
        editor.delete_model(model)
