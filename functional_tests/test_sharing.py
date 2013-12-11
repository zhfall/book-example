from selenium import webdriver
from .base import FunctionalTest

def quit_if_possible(browser):
    try: browser.quit()
    except: pass


class HomePage(object):

    def __init__(self, test):
        self.test = test
        #self.browser = test.browser

    def start_new_list(self, first_item_text):
        self.test.get_item_input_box().send_keys(first_item_text + '\n')
        self.test.wait_for_page_to_contain(first_item_text)
        ListPage(self.test).check_for_row_in_list_table(first_item_text, 1)


class ListPage(object):
    def __init__(self, test):
        self.test = test
        self.browser = test.browser


    def check_for_row_in_list_table(self, expected_text, pos):
        self.test.wait_for_page_to_contain(expected_text)
        table = self.browser.find_element_by_id('id_list_table')
        expected_row = '{}: {}'.format(pos, expected_text)
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(expected_row, [row.text for row in rows])


    def get_share_email_input(self):
        return self.test.browser.find_element_by_css_selector(
            'input[name=email]'
        )


    def check_share_email_input_placeholder(self):
        share_input = self.get_share_email_input()
        self.assertEqual(
            share_input.get_attribute('placeholder'),
            'your@friends-email.com'
        )


    def get_shared_with_emails(self):
        email_items = self.test.browser.find_elements_by_css_selector(
            'li.sharee-email'
        )
        return [li.text for li in email_items]


    def wait_for_list_to_be_shared_with(self, email):
        self.test.wait_for(
            lambda: self.assertIn(email, self.get_shared_with_emails())
        )


    def share_list_with(self, email):
        share_input = self.get_share_email_input()
        share_input.send_keys(email)
        self.wait_for_list_to_be_shared_with(email)



class MyListsPage(object):

    def __init__(self, test):
        self.test = test
        self.browser = test.browser

    def go_to_my_lists_page(self):
        self.test.browser.get(self.test.server_url)
        self.browser.find_element_by_link_text('My lists').click()
        self.test.wait_for_page_to_contain('My lists')


    def get_shared_lists(self):
        lists = self.test.browser.find_elements_by_css_selector(
            'li.shared-list'
        )
        return [li.text for li in lists]


    def wait_for_shared_list(self, list_title, list_owner):
        expected_row = '{} ({})'.format(list_title, list_owner)
        self.test.wait_for(
            lambda: self.assertIn(expected_row, self.get_shared_lists())
        )





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
        self.browser.get(self.server_url)
        HomePage(self).start_new_list('Get help')

        # She notices a "Share this list" option
        list_page = ListPage(self)
        list_page.check_share_email_input_placeholder()


        # She fills in Oniciferous's email, and the page updates
        # to say the list is shared with him
        list_page.share_list_with('oniciferous@email.com')

        # Oniciferous now goes to his "My lists" page with his browser
        self.browser = oni_browser
        my_lists_page = MyListsPage(self)
        my_lists_page.go_to_my_lists_page()

        # He sees Edith's list in there!
        my_lists_page.wait_for_shared_list('Get help', 'edith@email.com')

        # He clicks through to it, and can see that it's Edith's list
        self.browser.find_element_by_link_text('Get help').click()

        self.wait_for(
            lambda: self.assertIn(
                'List owner: edith@email.com',
                self.browser.find_element_by_tag_name('body').text
            )
        )

        # He adds an item to the list
        self.get_item_input_box().send_keys('Hi Edith!\n')

        # When edith refreshes the page, she sees Oniciferous's addition
        self.browser = edith_browser
        self.browser.refresh()
        self.check_for_row_in_list_table('2: Hi Edith!')

