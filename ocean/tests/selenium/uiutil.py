#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from selenium.webdriver.support.ui import Select, WebDriverWait as Wait
from selenium.common.exceptions import TimeoutException

class FrontendError(Exception):
    pass

def MapPortalDriver(base, **kwargs):
    return type('MapPortalDriver', (_BaseMapPortalDriver, base), kwargs)

class _BaseMapPortalDriver(object):
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
        except (TimeoutException, FrontendError) as e:
            # do we have an error dialog
            dialog = self.find_element_by_id('error-dialog')
            if dialog.is_displayed():
                content = dialog.find_element_by_id('error-dialog-content')
                raise FrontendError(content.text)
            else:
                raise e

    def find_elements_by_jquery(self, jq):
        return self.execute_script('''return $('%s').get();''' % jq)

    def find_element_by_jquery(self, jq):
        elems = self.find_elements_by_jquery(jq)
        assert len(elems) == 1
        return elems[0]

def output(src):
    def __call__(browser):
        dialog = browser.find_element_by_id('error-dialog')
        if dialog.is_displayed():
            raise FrontendError()

        outputDiv = browser.find_element_by_id('outputDiv')
        output = outputDiv.find_element_by_tag_name('img')
        return src in output.get_attribute('src')

    return __call__

def jquery(jq):
    def __call__(browser):
        dialog = browser.find_element_by_id('error-dialog')
        if dialog.is_displayed():
            raise FrontendError()

        elems = browser.find_elements_by_jquery(jq)
        return elems > 0

    return __call__

def animation_finished(browser):
    return browser.execute_script('''return $(':animated').length''') == 0
