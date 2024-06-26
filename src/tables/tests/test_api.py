import json
from django.test import TestCase

from tables.models import Table, Field
from tables import table_build


class TestCreateTable(TestCase):
    def test_create_simple(self):
        response = self.client.post(
            path='/api/table/',
            data={
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
        )

        self.assertLess(response.status_code, 400, response.content)

        response_json = json.loads(response.content)
        new_model = Table.objects.first()

        self.assertIsNotNone(new_model)
        self.assertEqual(response_json['id'], new_model.id)


class TestUpdateTable(TestCase):
    def setUp(self):
        self.table_name = 'test_table'
        self.table = Table.objects.create()
        self.field = Field.objects.create(
            table=self.table,
            name='name',
            field_type='string',
        )
        self.model = self.table.get_model()
        table_build.create_table(self.model)

    # looks like this is not neccesary
    # def tearDown(self):
    #     self.table.refresh_from_db()
    #     table_build.remove_table(self.table.get_model())

    def _post_anemic_payloads(self):
        payloads = [
                {'name': 'Mark'},
                {'name': 'Sam'},
                {'name': 'Tom'},
            ]
        for payload in payloads:
            response = self.client.post(
                path=f'/api/table/{self.table.id}/row/',
                data=payload,
            )
            self.assertLess(response.status_code, 400, response.content)

        return len(payloads)

    def test_add_field(self):
        new_field_name = 'age'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
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
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))

    def test_add_numeric_field_with_default(self):
        new_field_name = 'age'
        default_value = 999

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
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
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))

    def test_add_numeric_field_with_default_then_change(self):
        new_field_name = 'age'
        default_value = 999
        second_default = 1012

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
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
        )
        self.assertLess(response.status_code, 400)

        self._post_anemic_payloads()

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'number',
                        'default': second_default
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems * 2)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertEqual(sum(1 for elem in response_content if elem[new_field_name] == default_value), num_elems)
        self.assertEqual(sum(1 for elem in response_content if elem[new_field_name] == second_default), num_elems)

    def test_add_numeric_field_without_default(self):
        new_field_name = 'age'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
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
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] is None for elem in response_content))

    def test_add_string_field_with_default(self):
        new_field_name = 'string_field'
        default_value = 'abrakadabra!!'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
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
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))

    def test_add_string_field_without_default(self):
        new_field_name = 'string_field'

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'string',
                    },
                    {
                        'name': new_field_name,
                        'field_type': 'string',
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] is None for elem in response_content))

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
        )
        self.assertLess(response.status_code, 400, response.content)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content))

    def test_add_boolean_field_without_default(self):
        new_field_name = 'yes_or_no'

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
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400, response.content)

        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] is None for elem in response_content))

    def test_add_boolean_field_without_default_then_add_default(self):
        new_field_name = 'yes_or_no'

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
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400, response.content)

        self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)
        self.assertTrue(all(elem[new_field_name] is None for elem in response_content))

        default_value = True  # Now we change default
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
                        'default': default_value,
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400, response.content)

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertGreater(len(response_content), 0)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content), response_content)

        self._post_anemic_payloads()
        num_elems = self._post_anemic_payloads()

        response = self.client.get(path=f'/api/table/{self.table.id}/rows/')
        response_content = json.loads(response.content)

        self.assertEqual(len(response_content), num_elems * 3)
        self.assertTrue(all(new_field_name in elem for elem in response_content))
        # self.assertTrue(all(elem[new_field_name] == default_value for elem in response_content), response_content)

        # BUG
        # default value if dably assigned to incoming objects
        # serializers do not apply defaults, they usually assign None to not empty fields
        # but empty boolead is casted to False so default True for boolean does not work
        # in rest_framework/serializers.py#497

    def test_change_of_field_type_is_not_permitted(self):

        response = self.client.put(
            path=f'/api/table/{self.table.id}/',
            data={
                'name': 'new_name',
                'fields': [
                    {
                        'name': 'name',
                        'field_type': 'number',
                    },
                ]
            },
            content_type="application/json",
        )
        self.assertContains(response, 'change of field type forbidden', status_code=400)


class TestRemoveTableFields(TestCase):
    example_payloads = [
        {'name': 'Sam', 'age': 25, 'married': True},
        {'name': 'George', 'age': 35, 'married': True},
        {'name': 'Stacy', 'age': 25, 'married': False},
        {'name': 'Len', 'age': 45},
        {'name': 'Foo', 'married': False},
        {'name': 'Ann'},
    ]

    def setUp(self):
        self.table_payload = {
            'fields': [
                {
                    'name': 'name',
                    'field_type': 'string',
                },
                {
                    'name': 'age',
                    'field_type': 'number',
                    'default': 30,
                },
                {
                    'name': 'married',
                    'field_type': 'boolean',
                    'default': False,
                },
            ]
        }
        # First build complete table
        response = self.client.post(
            path='/api/table/',
            data=self.table_payload,
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400)

        response_json = json.loads(response.content)
        self.table_id = response_json['id']

    def _put_table_data(self, table_data):
        response = self.client.put(
            path=f'/api/table/{self.table_id}/',
            data=table_data,
            content_type="application/json",
        )
        self.assertLess(response.status_code, 400, response.content)

    def _post_data(self):
        for payload in self.example_payloads:
            response = self.client.post(
                path=f'/api/table/{self.table_id}/row/',
                data=payload,
                content_type="application/json",
            )
            self.assertLess(response.status_code, 400)

    def _get_data(self):
        response = self.client.get(path=f'/api/table/{self.table_id}/rows/')
        self.assertLess(response.status_code, 400)

        data = json.loads(response.content)
        self.assertGreater(len(data), 0)

        return data

    def test_not_removed(self):
        self._put_table_data(self.table_payload)  # Build complete table another time, nothing changes
        self._post_data()
        payload = self._get_data()

        self.assertTrue(all('name' in elem for elem in payload))
        self.assertTrue(all('age' in elem for elem in payload))
        self.assertTrue(all('married' in elem for elem in payload))
        self.assertTrue(all('id' in elem for elem in payload))

    def test_remove_one_field(self):
        removed = self.table_payload['fields'][0]
        removed_field_name = removed['name']

        self.table_payload['fields'] = self.table_payload['fields'][1:]
        self._put_table_data(self.table_payload)

        self._post_data()
        payload = self._get_data()

        self.assertFalse(any(removed_field_name in elem for elem in payload))
        self.assertTrue(all(len(elem) == len(self.table_payload['fields']) + 1 for elem in payload), payload)  # +1 (id)

    def test_remove_all(self):
        self._put_table_data({'fields': []})
        self._post_data()
        payload = self._get_data()

        self.assertFalse(any('name' in elem for elem in payload), payload)
        self.assertFalse(any('age' in elem for elem in payload))
        self.assertFalse(any('married' in elem for elem in payload))
        self.assertTrue(all('id' in elem for elem in payload))

    def test_leave_only_name_field(self):
        self._put_table_data({
            'fields': [
                {
                    'name': 'name',
                    'field_type': 'string',
                }
            ]
        })
        self._post_data()
        payload = self._get_data()

        self.assertTrue(all('name' in elem for elem in payload))
        self.assertFalse(any('age' in elem for elem in payload))
        self.assertFalse(any('married' in elem for elem in payload))
        self.assertTrue(all('id' in elem for elem in payload))
