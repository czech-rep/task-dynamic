import json
from django.test import TestCase

from tables.models import Table, Field
from tables import table_build


class TestCreateTable(TestCase):
    def test_create_simple(self):
        response = self.client.post(
            path='/api/table/',
            data={
                'name': 'test_table_1',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': 'age',
                        'field_type': 'number',
                        'default': 5
                    },
                ]
            },
            content_type="application/json",
            follow=True,
        )

        self.assertLess(response.status_code, 400)

        response_json = json.loads(response.content)
        new_model = Table.objects.first()

        self.assertIsNotNone(new_model)
        self.assertEqual(new_model.name, 'test_table_1')
        self.assertEqual(response_json['id'], new_model.id)

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

# class TestEmptyTable(TestCase):


class TestUpdateTable(TestCase):
    def setUp(self):
        self.table_name = 'test_table'
        self.table = Table.objects.create(name=self.table_name)
        self.field = Field.objects.create(
            table=self.table,
            name='name',
            field_type='string',
        )
        self.model = table_build.get_model(self.table)
        table_build.create_table(self.model)

    def tearDown(self):
        self.table.refresh_from_db()
        table_build.remove_table(table_build.get_model(self.table))

    def test_add_field(self):
        new_field_name = 'age'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'name': 'new_name',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'number',
                    },
                ]
            },
            content_type="application/json",
            follow=True,
        )

        self.assertLess(response.status_code, 400)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Mark', 'age': 30},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400, response.content)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Sam', 'age': 40},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400)

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertTrue(all(new_field_name in elem for elem in response_content))

    def test_add_numeric_field_with_default(self):
        new_field_name = 'age'
        default_value = 999

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'name': 'new_name',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'number',
                        'default': default_value
                    },
                ]
            },
            content_type="application/json",
            follow=True,
        )

        self.assertLess(response.status_code, 400)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Mark'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400, response.content)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Sam'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400)

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))

    def test_add_string_field_with_default(self):
        new_field_name = 'string_field'
        default_value = 'abrakadabra!!'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'name': 'new_name',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'string',
                        'default': default_value
                    },
                ]
            },
            content_type="application/json",
            follow=True,
        )

        self.assertLess(response.status_code, 400)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Mark'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400, response.content)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Sam'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400)

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))

    def test_add_boolean_field_with_default(self):
        new_field_name = 'yes_or_no'
        default_value = False

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'name': 'new_name',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'boolean',
                        'default': default_value
                    },
                ]
            },
            content_type="application/json",
            follow=True,
        )

        self.assertLess(response.status_code, 400, response.content)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Mark'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400, response.content)

        response = self.client.post(
            path=f'/api/table/{self.table.id}/row/',
            data={'name': 'Sam'},
            content_type="application/json",
            follow=True,
        )
        self.assertLess(response.status_code, 400)

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))


# create a table with one row
# add each of field types
# post data with added column
#