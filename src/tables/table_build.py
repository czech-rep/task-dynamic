from django.db import models, connection

from tables.models import Table, Field



def get_model_changes(model_before, model_after):
    models_fields = lambda model: {field.name: field for field in model._meta.fields}

    model_before = models_fields(model_before)
    model_after = models_fields(model_after)

    for new_field in model_after.keys() - model_before.keys():
        yield 'add_field', model_after[new_field]

    for removed_field in model_before.keys() - model_after.keys():
        yield 'remove_field', model_before[removed_field]

    for common_field in model_before.keys() & model_after.keys():
        field_old = model_before[common_field]
        field_new = model_after[common_field]
        # Here compare for changes to be handled
        # null
        # default - but this change is only in django model, not in db
        # TODO could handle index, verbose name, unique...
        if (
            field_old.null != field_new.null
            or field_old.default != field_new.default
        ):
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
                    editor.alter_field(model, *args)
                case _:
                    raise ValueError(f'unhandled {change}')


def create_table(model):
    with connection.schema_editor() as editor:
        editor.create_model(model)


def remove_table(model):
    with connection.schema_editor() as editor:
        editor.delete_model(model)
