---
layout: post
comments: true
title: "Selenium"
tags: [selenium,unit tests,python]
---

## Move the mouse over an element

```
ActionChains(self.selenium).move_to_element(element).perform()
```

## Set chrome executable path

```
opts = webdriver.ChromeOptions()
opts.binary_location(value='/usr/bin/chrome')
cls.selenium = WebDriver(opts=opts)
```

## Execute javascript

```
self.selenium.execute_script('var miao = 1;')
```

## Insert text into inputs

```
password_input.send_keys('...')
self.selenium.find_element_by_xpath('//button[text()="Log in"]').click()
```

## Wait loader

```
element = WebDriverWait(self.selenium, 10)\
    .until(expected_conditions.invisibility_of_element_located((By.ID, 'modal')))
```

## Retrieve value from input

```
element.get_attribute('value')
```

## Go to page

```
self.selenium..get('%s%s' % (self.live_server_url, reverse('app:view')))
```

## Accessing browser's log

This is not available in all the browsers.

```
self.selenium.get_log('browser')
```

```
def tearDown(self):
    logger.debug('remove old JS log %s' % self.selenium.get_log('browser'))
```

## Click at the center of the screen

```
body = self.selenium.find('body')
size = body.size
actions = ActionChains(self.selenium)\
    .move_to_element_with_offset(body, size['width']/2, size['height']/2)\
    .click()

actions.perform()
```

## XPath reference

