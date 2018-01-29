# -*- coding: utf-8 -*-
# System imports
import time
import unittest
import urllib2

# 3rd party imports
from flask import Flask
from parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USE_REMOTE_WEB_DRIVER = True  # don't set to False, unless you want to use a VirtualEnv

# HOST (IP) where the website instance is running. It *should* begin with 'localhost' if you are on linux OS. See the IP
# address where docker is running and put that here. For OS X, the public IP of the host should work.
DOCKER_HOST = "192.168.99.100"
# 0.0.0.0 seems to work universally, whereas localhost:4444 had some trouble on OS X.
SELENIUM_REMOTE_HOST = '0.0.0.0:4444'


test_s = "test"
unmatching_s = "foo"
similar_s = "est"
similar_s2 = "tet"

large_s1 = "CTGTGTGCAGATGGGGCGACGAGACACTGGCCCTGATTTCTCCGCTTCTAATAGCACACACCGGGCAATACGAGCTCAAGCCAGTCTCGCAGTAACGCTCA" \
           "TCAGCAAACGAAAGAGTTTAAGGCTCGCTAATTCGCACTGTCAGGGTCCCTTGGGTGTTTTGCACTAGCGTCAGGTAGGCTAGTATGTGTTTTTCCTTC"

large_s2 = "CAGGGGTATGTGGCTGCGTGGTCAAATGTGCGGCATACGTATTTGCTCGGCGTGCTTGCTCTCACGAACTTGACCTGGAGATCAAGGAGATGTTTCTTGTC" \
           "CAACTGGACAGCGCTTCAACGGAATGGATCTACGTTACAGCCTGCATAAAGAAAACGGAGTTGCCGAGGACGAAAGCGACTTTAGGTTCTGTCCGTTGT"

LEVEN='levenshtein'
JAC='jaccard'
HAM='hamming'


class TestCase(unittest.TestCase):

    def create_app(self):
        app = Flask(__name__)

        app.config['TESTING'] = True

        app.config['LIVESERVER_PORT'] = 4000  # Linux OS
        # app.config['LIVESERVER_PORT'] = 5000  # Win OS

        return app

    # Open the Browser, go to the running site
    def setUp(self):

        if USE_REMOTE_WEB_DRIVER:
            self.driver = webdriver.Remote(
                command_executor='http://' + SELENIUM_REMOTE_HOST + ':4444/wd/hub',
                desired_capabilities=DesiredCapabilities.FIREFOX)

        else:
            self.driver = webdriver.Firefox()

        self.driver.get("http://" + DOCKER_HOST + ":4000")  # Linux (Docker)
        # self.driver.get("http://0.0.0.0:80")  # Linux local
        # self.driver.get("http://127.0.0.1:5000")  # Win OS

    def tearDown(self):
        try:
            self.driver.quit()
            self.driver.close()
        except:
            pass  # fail silently, we just want the browser closing here, not for us to test

    def test_server_is_running(self):
        response = urllib2.urlopen("http://" + DOCKER_HOST + ":4000")
        self.assertEqual(response.code, 200)

    @parameterized.expand([
        (LEVEN + '_similar', LEVEN, test_s, similar_s, '1'),
        (LEVEN + '_same', LEVEN, test_s, test_s, '0'),
        (LEVEN + '_nomatch', LEVEN, test_s, unmatching_s, str(len(test_s))),
        # 105 comes from external website calculation
        (LEVEN + '_large', LEVEN, large_s1, large_s2, '105'),
        (HAM + '_same', HAM, test_s, test_s, '0'),
        (HAM + '_similar', HAM, similar_s, similar_s2, '2'),
        (JAC + '_same', JAC, test_s, test_s, '1.0'),
        (JAC + '_nomatch', JAC, test_s, unmatching_s, '0.0'),
        (JAC + '_large', JAC, large_s1, large_s2, '1.0'),
    ])
    def test_metric(self, name, metric, s1, s2, result):
        self.assertEqual(self._run_metric(metric, s1, s2, 'result-num'), result)

    @parameterized.expand([
        (HAM, test_s, similar_s, 'metric-err', 'must be the same length'),
        (JAC, "", large_s2, 'string_1-err', 'required'),
    ])
    def test_metric_err(self, metric, s1, s2, errorclass, msg):
        self.assertIn(msg, self._run_metric(metric, s1, s2, errorclass))

    def _run_metric(self, metric, s1, s2, resultclass):
        self.driver.find_element_by_id('string_1').send_keys(s1)
        self.driver.find_element_by_id('string_2').send_keys(s2)
        select = Select(self.driver.find_element_by_id('metric'))
        select.select_by_value(metric)
        self.driver.find_element_by_id('submit_btn').click()
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, resultclass)))
        return self.driver.find_element_by_class_name(resultclass).text

    @parameterized.expand([
        (HAM, test_s, similar_s, 'metric-err'),
        (JAC, "", large_s2, 'string_1-err'),
    ])
    def test_ham_length_error_no_result(self, metric, s1, s2, errclass):
        self._run_metric(metric, s1, s2, errclass)
        with self.assertRaises(NoSuchElementException) as nse:
            self.driver.find_element_by_class_name('result-num')

if __name__ == '__main__':
    unittest.main()
