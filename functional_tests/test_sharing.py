from selenium import webdriver
from .base import FunctionalTest

class SharingTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@email.com')

        # She goes to the home page and starts a list
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Get help\n')

        # She notices a "Share this list" icon
        self.browser.find_element_by_id('id_share_this_list_button').click()

        # A share dialog pops up.
        # She decides to share with her friend Oniciferous
        self.browser.find_element_by_css_selector('input[name=email]').send_keys(
            'oniciferous@email.com\n'
        )

        # Oniciferous comes along in a different browser, also logged in
        ediths_browser = self.browser
        self.browser = webdriver.Firefox()
        self.create_pre_authenticated_session('oniciferous@email.com')

        # Oniciferous goes to the lists page
        self.browser.find_element_by_link_text('My lists').click()

        # He sees edith's list in there!
        self.browser.find_element_by_link_text('Get help').click()

        # It says that it's edith's list
        self.wait_for(
            lambda: self.assertIn(
                'edith@email.com',
                self.browser.find_element_by_name('body').text
            )
        )

        # He adds an item to the list
        self.get_item_input_box().send_keys('Hi Edith!')

        # When edith refreshes the page, she sees Oniciferous's addition
        onis_browser = self.browser
        self.browser = ediths_browser
        self.browser.refresh()
        self.browser.find_elements_by_link_text('Hi Edith!')

