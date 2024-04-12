# import random
# import string
# from django.test import TestCase

# from tables.models import Table, Field
# from tables import table_build


# """test our code what enables to create any Table and reflect it in db"""


# class TestBuildier(TestCase):
#     def setUp(self):
#         self.table = Table.objects.create()
#         self.fields = [
#             Field.objects.create(
#                 table=self.table,
#                 name="".join(random.choice(string.ascii_lowercase) for _ in range(5)),
#                 field_type=random.choice(Field.FieldType.choices)[0]
#             ) for _ in range(4)
#         ]

#         self.model = table_build.get_model(self.table)
#         table_build.create_table(self.model)

#     def tearDown(self):
#         table_build.remove_table(self.model)

#     def test_tables_model(self):
#         self.assertEqual(self.model._meta.app_label, 'tables')
#         self.assertEqual(self.model.__name__, self.table.name)

#         self.assertEqual(
#             set(field.name for field in self.model._meta.fields),
#             set(field.name for field in self.table.fields.all()) | {'id'},
#         )

#     def test_add_field(self):
#         format_first = self.table.compare_format()
#         new_field = Field.objects.create(
#             table=self.table,
#             name='field5',
#             field_type='boolean',
#         )
#         self.table.refresh_from_db()

#         changes = list(table_build.get_changes(format_first, self.table.compare_format()))
#         self.assertEqual(changes[0][0], 'add_field')

#         # table_build.alter_table(self.model, changes)
#         self.model = table_build.get_model(self.table)
#         # TODO check thats in real table
#         self.assertIn('field5', [field.name for field in self.model._meta.fields])

#     def test_remove_field(self):
#         pass

#     def test_change_field_type(self):
#         pass
