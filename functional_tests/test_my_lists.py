from .base import FunctionalTest
from .home_and_list_pages import HomePage

class MyListsTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session(email='edith@email.com')

        # She goes to the home page and starts a list
        list_page = HomePage(self).start_new_list('Reticulate splines')
        list_page.add_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # She notices a "My lists" link, for the first time.
        self.browser.find_element_by_link_text('My lists').click()

        # She sees that her list is in there, named according to its
        # first list item
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.current_url, first_list_url
        ))

        # She decides to start another list, just to see
        self.start_new_list('Click cows')
        second_list_url = self.browser.current_url

        # Under "my lists", her new list appears
        self.browser.find_element_by_link_text('My lists').click()
        self.browser.find_element_by_link_text('Click cows').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.current_url, second_list_url
        ))

        # She logs out.  The "My lists" option disappears
        self.browser.find_element_by_id('id_logout').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_elements_by_link_text('My lists'),
            []
        ))

