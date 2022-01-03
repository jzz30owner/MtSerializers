import unittest
import serilizer
import datetime


class SerializerTestCase(unittest.TestCase):

    def test_check_string_field(self):

        class TestModel(serilizer.BaseSerializer):
            name = serilizer.String(length=5)

        test_string = "hello"

        ob = TestModel()
        ob.name = test_string
        data = ob.get_data()

        self.assertEqual(ob.name, test_string)
        self.assertEqual(data.name.decode(), test_string)

    def test_check_empty_integers(self):

        class TestModel(serilizer.BaseSerializer):
            number = serilizer.Int32()

        tm = TestModel()

        self.assertIsInstance(tm.number, int)
        self.assertEqual(tm.number, 0)

    def test_check_empty_floats(self):
        class TestModel(serilizer.BaseSerializer):
            number = serilizer.Float32()

        tm = TestModel()

        self.assertIsInstance(tm.number, float)
        self.assertEqual(tm.number, 0)

    def test_check_bool(self):
        class TestModel(serilizer.BaseSerializer):
            flag = serilizer.Bool()

        tm = TestModel()

        self.assertIsInstance(tm.flag, bool)
        self.assertFalse(tm.flag)

    def test_datetime_field(self):

        class TestModel(serilizer.BaseSerializer):
            dt = serilizer.Datetime()

        expected = datetime.datetime.now()
        test_obj = TestModel()
        test_obj.dt = expected

        self.assertIsInstance(test_obj.dt, datetime.datetime)
        self.assertEqual(expected, test_obj.dt)

    def test_datetime_empty_buffer(self):

        class TestModel(serilizer.BaseSerializer):
            dt = serilizer.Datetime()

        expected = datetime.datetime(1970, 1, 1, 4, 0)
        ob = TestModel()

        self.assertIsInstance(ob.dt, datetime.datetime)
        self.assertEqual(ob.dt, expected)


class ListSerializerTestCase(unittest.TestCase):

    def setUp(self) -> None:

        class TestObject(serilizer.BaseSerializer):
            a = serilizer.Int32()
            b = serilizer.Int32()

        self.model_class = TestObject
        self.size = 2
        self.buffer = memoryview(bytearray((255, 0, 0, 0, 100, 0, 0, 0) * self.size))

    def test_correct_size(self):
        l = serilizer.ListSerializer(self.model_class, self.buffer)
        self.assertEqual(len(l), self.size)

    def test_check_objects(self):
        l = serilizer.ListSerializer(self.model_class, self.buffer)
        for i in l:
            self.assertEqual(i.a, 255)
            self.assertEqual(i.b, 100)

    def test_wrong_buffer(self):
        buff = memoryview(bytearray([]))
        l = serilizer.ListSerializer(self.model_class, buff)
        self.assertEqual(len(l), 0)