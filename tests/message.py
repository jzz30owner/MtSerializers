import asyncio
from typing import Type
import unittest
from src.mt4_utils import serializer, message


class MessageTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.dispatcher = message.Dispatcher()
        self.async_dispatcher = message.AsyncDispatcher()

    def test_dispatcher_callback_wrapper(self):

        class TestModel(serializer.BaseSerializer):
            status = serializer.Int32()

        @self.dispatcher.callback(message_code=99)
        def test_func(data: TestModel) -> TestModel:
            return data

        callback = self.dispatcher._callbacks[99]
        self.assertIsNotNone(callback)

    def test_dispatcher_wrapper_callbacks_mapper(self):

        class TestModel(serializer.BaseSerializer):
            size = 7
            status = serializer.String(length=5)

        class TestModel2(serializer.BaseSerializer):
            code = serializer.Int32()

        @self.dispatcher.callback(message_code=1)
        def test_func(data: TestModel) -> TestModel:
            self.assertEqual(data.status, "Hello")
            return data

        @self.dispatcher.callback(message_code=3)
        def test_func3(data: serializer.ListSerializer[TestModel]) -> serializer.ListSerializer[TestModel]:
            return data

        @self.dispatcher.callback(message_code=2)
        def test_func2(data: TestModel2) -> TestModel2:
            return data

        payload1 = b"Hello"
        payload2 = b"\xFF\x00\x00\x00"

        response1 = self.dispatcher.invoke(1, payload1)
        response2 = self.dispatcher.invoke(2, payload2)

        self.assertIsInstance(response1, TestModel)
        self.assertIsInstance(response2, TestModel2)

        self.assertEqual(response1.status, "Hello")
        self.assertEqual(response2.code, 255)

        payload3 = b"Helloff"*3
        response1 = self.dispatcher.invoke(3, payload3)
        response1.get_objects()

    def test_async_invoker(self):

        class TestModel(serializer.BaseSerializer):
            status = serializer.String(length=5)

        @self.async_dispatcher.callback(message_code=1)
        async def test_func(data: TestModel) -> TestModel:
            return data

        async def async_task():
            response1 = await self.dispatcher.invoke(1, payload1)
            self.assertIsInstance(response1, TestModel)
            self.assertEqual(response1.status, "Hello")

        payload1 = b"Hello"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_task())

    def test_account_in_params(self):

        class Test(serializer.BaseSerializer):
            code = serializer.Int32()

        @self.dispatcher.callback(message_code=10)
        def test_func(data: Test, account_id: int):
            self.assertEqual(data.code, 100)
            self.assertIsNotNone(account_id)
            self.assertIsInstance(account_id, int)
            self.assertEqual(account_id, 10)

        payload = int(100).to_bytes(byteorder="little", signed=True, length=4)
        self.dispatcher.invoke(10, payload, account_id=10)

    def test_account_in_params_none(self):

        class Test(serializer.BaseSerializer):
            code = serializer.Int32()

        @self.dispatcher.callback(message_code=10)
        def test_func(data: Test, account_id: int):
            self.assertIsNone(account_id)

        payload = int(100).to_bytes(byteorder="little", signed=True, length=4)
        self.dispatcher.invoke(10, payload)
