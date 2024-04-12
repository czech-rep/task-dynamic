from django.db import models, connection

from tables.models import Table, Field


# provided Table instance with its Fields
# we need to assemble Model class and then create and migrate it

def field_instance(field_attrs: dict):
    """based on fmt() dict"""

    if field_attrs['default'] is None:
        field_attrs.pop('default')
        field_attrs['null'] = True
    print('---attrs', field_attrs)

    field_type = field_attrs.pop('field_type')

    match field_type:
        case Field.FieldType.string:
            field = models.CharField(**field_attrs)
        case Field.FieldType.number:
            field = models.IntegerField(**field_attrs)
        case Field.FieldType.boolean:
            field = models.BooleanField(**field_attrs)
        case _:
            raise ValueError(f'{field_type} not handled')

    field.column = field.db_column
    return field


def get_model(table):
    attrs = {field.name: field_instance(field.fmt()) for field in table.fields.all()}
    attrs['get_fields'] = lambda x: {field.name: field for field in x._meta.fields}

    attrs['__module__'] = 'tables.models'

    model = type(
        table.name,
        (models.Model, ),
        attrs,
    )

    model._meta.db_table = table.name

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

    # if m1['name'] != m2['name']:
        # yield 'alter_db_table', custom_table_name(m1['name']), custom_table_name(m2['name']) # here real names
        # alter_db_table_comment(model, old_db_table_comment, new_db_table_comment)
    print(m1)
    print(m2)

    new_fields = m2.keys() - m1.keys()
    removed_fields = m1.keys() - m2.keys()
    common_fields = m1.keys() & m2.keys()
    print(new_fields, removed_fields, common_fields)

    for new_field in new_fields:
        field_data = m2[new_field]
        yield 'add_field', field_data
    for removed_field in removed_fields:
        field_data = m1[removed_field]
        yield 'remove_field', field_data
    for common_field in common_fields:
        field_old = m1[common_field]
        field_new = m2[common_field]
        print(field_new)
        # from default before comparing becouse its not reflected in db. But null is
        if field_old.null != field_new.null:
            # print('difference by null', field_old.null, field_new.null)
            yield 'alter_field', field_old, field_new


def alter_table(model, changes):
    with connection.schema_editor() as editor:
        for change, *args in changes:
            match change:
                case 'add_field':
                    editor.add_field(model, *args)
                case 'remove_field':
                    editor.remove_field(model, *args)
                case 'alter_field':

                    f1, f2 = args
                    # f1.concrete = False
                    print('name', f2.name)
                    # f2.contribute_to_class(model, f2.name)
                    print(f1.column, f2.column)
                    print(f1.null, f2.null)
                    print(model._meta.fields)

                    editor.alter_field(model, f1, model._meta.fields[-1])
                case _:
                    raise ValueError(f'unhandled {change}')


def create_table(model):
    with connection.schema_editor() as editor:
        editor.create_model(model)


def remove_table(model):
    with connection.schema_editor() as editor:
        editor.delete_model(model)
