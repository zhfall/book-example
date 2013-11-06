from datetime import datetime
from selenium import webdriver
import sys
import time

from django.test import LiveServerTestCase
from .server_tools import reset_database

DEFAULT_WAIT = 3


class FunctionalTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_host = arg.split('=')[1]
                cls.server_url = 'http://' + cls.server_host
                cls.against_staging = True
                return
        LiveServerTestCase.setUpClass()
        cls.against_staging = False
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            LiveServerTestCase.tearDownClass()

    def setUp(self):
        if self.against_staging:
            reset_database(self.server_host)

        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        if not self._outcomeForDoCleanups.success:
            self.take_screenshot()
            self.dump_html()

        self.browser.quit()
        super().tearDown()


    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')
        return '{}.{}-{}'.format(
            self.__class__.__name__, self._testMethodName, timestamp
        )


    def take_screenshot(self):
        filename = 'seleniumscreenshot-{}.png'.format(self._get_filename())
        print('screenshotting to', filename)
        self.browser.get_screenshot_as_file(filename)


    def dump_html(self):
        filename = 'seleniumhtml-{}.html'.format(self._get_filename())
        print('dumping page HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)


    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
        start_time = time.time()
        while True:
            try:
                return function_with_assertion()
            except AssertionError:
                if time.time() - start_time > timeout:
                    raise


    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')


    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

