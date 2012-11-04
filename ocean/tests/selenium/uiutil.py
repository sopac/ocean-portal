
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait as Wait
from selenium.common.exceptions import TimeoutException

class FrontendError(Exception):
    pass

class MapPortalDriver(webdriver.Firefox):

    def select_param(self, id, text):
        select = Select(self.find_element_by_id(id))
        select.select_by_visible_text(text)

    def ensure_selected(self, id, text, noptions=None):
        select = Select(self.find_element_by_id(id))
        option = select.first_selected_option
        assert option.text == text

        # FIXME: broken
        # if noptions is not None:
        #     options = filter(lambda o: o.is_displayed(), select.options)
        #     assert len(options) == noptions

    def submit(self):
        self.find_element_by_id('submit').click()

    def wait(self, event, timeout=10):
        try:
            Wait(self, timeout).until(event)
        except TimeoutException as e:
            # do we have an error dialog
            dialog = self.find_element_by_id('error-dialog')
            if dialog.is_displayed():
                content = dialog.find_element_by_id('error-dialog-content')
                raise FrontendError(content.text)
            else:
                raise e

def output(src):
    def __call__(browser):
        outputDiv = browser.find_element_by_id('outputDiv')
        output = outputDiv.find_element_by_tag_name('img')
        dialog = browser.find_element_by_id('error-dialog')
        return src in output.get_attribute('src') or \
               dialog.is_displayed()

    return __call__
