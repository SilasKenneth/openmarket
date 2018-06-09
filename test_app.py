from unittest import TestCase
import unittest
import httplib2
http = httplib2.Http()
class TestApp(TestCase):
    def test_works(self):
        res,headers = http.request("http://localhost:3000","GET")
        ans = headers.decode("utf-8")
        self.assertEqual(ans, "hello".strip())
    def test_traders(self):
        res,headers = http.request("http://localhost:3000/trader/login","GET")
        ans = headers.decode("utf-8")
        print(ans)
        self.assertEqual(ans, None)
def main():
    unittest.main()

if __name__ == '__main__':
    main()