from selenium import webdriver
from .base import FunctionalTest
from .home_and_list_pages import HomePage

def quit_if_possible(browser):
    try: browser.quit()
    except: pass

from django.test.testcases import WSGIRequestHandler
from django.test.utils import override_settings
from unittest.mock import patch

def debuggable(test_method_or_class):
    from django.conf import settings
    settings.MEDIA_URL = '/media/'
    return patch(
        'django.test.testcases.QuietWSGIRequestHandler.log_message',
        WSGIRequestHandler.log_message
    )(override_settings(DEBUG=True)(test_method_or_class))


@debuggable
class SharingTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@email.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Oniciferous is also hanging out on the lists site
        oni_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.create_pre_authenticated_session('oniciferous@email.com')

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        list_page = HomePage(self).start_new_list('Get help')

        # She notices a "Share this list" option
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your@friends-email.com'
        )

        # She shares her list.
        # The page updates to say that it's shared with Oniciferous:
        list_page.share_list_with('oniciferous@email.com')


        # Oniciferous now goes to the 'My lists' page with his browser
        self.browser = oni_browser
        home_page = HomePage(self).go_to_home_page()
        home_page.go_to_my_lists_page()

        # He sees Edith's list in there!
        self.browser.find_element_by_link_text('Get help').click()

        # On the list page, Oniciferous can see says that it's Edith's list
        self.wait_for(lambda: self.assertEqual(
            list_page.get_list_owner(),
            'edith@email.com'
        ))

        # He adds an item to the list
        list_page.add_new_item('Hi Edith!')

        # When Edith refreshes the page, she sees Oniciferous's addition
        self.browser = edith_browser
        self.browser.refresh()
        list_page.wait_for_new_item_in_list('Hi Edith!', 2)

