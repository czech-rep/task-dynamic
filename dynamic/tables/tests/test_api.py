from django.test import TestCase

from tables.models import Table, Field


# class TestCreateTable(TestCase):
#     def test_create_simple(self):
#         response = self.client.post(
#             '/api/table',
#             data={
#                 'name': 'People',
#             },
#             content_type='application/x-www-form-urlencoded',
#             follow=True,
#         )
#         print(response.content, response.status_code)
#         print(response.redirect_chain)
#         self.assertLess(response.status_code, 400)
#         new_model = Table.objects.first()
#         self.assertIsNotNone(new_model)
#         self.assertEqual(new_model.name, 'People')

    # def test_create(self):
    #     response = self.client.post(
    #         '/api/table',
    #         data={
    #             'name': 'People',
    #             'fields': {
    #                 'name': 'string',
    #                 'age': 'number',
    #             }
    #         },
    #     )

    #     self.assertLess(response.status_code, 400)
    #     new_model = Table.objects.first()

    #     self.assertIsNotNone(new_model)
    #     self.assertEqual(new_model.name, 'People')
        # self.assertEqual(new_model.name, 'People')


    # def test_update_table(self):
    #     pass