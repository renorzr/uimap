# uimap

Cross platform UI Automation Python Library

## Installation

    pip install uimap

## Usage

1. Create UI Map.
2. Load UI Map and access UI elements by names.

## Example
1. Create UI Map: c:\itunes.yml

        ---
        __driver: wpf
        WND_ITUNES:
          __char:
            __scope: child
            Name: iTunes
            ClassName: iTunes
            ControlType: Window
          LCD:
            __char:
              __scope: child
              Name: LCD 部分
              ControlType: Text
            LCD_DOWNLOADING: lbl正在下载*
            LCD_ACCESSING: lbl正在访问*
            LCD_PAYING: lbl正在购买*
            LCD_BTN_CANCEL: btn停止
          NAV_BAR:
            __char:
              __scope: child
              Name: ""
              ControlType: Button
            LNK_HOME:
              __char:
                __scope: child
                Name: iTunes Store 主页
                ControlType: Button

2. Load and access

        from uimap import UiMap
        ui = UiMap(r'c:\itunes.yml')
        if ui.WND_ITUNES.exist():
            print 'iTunes window is open.'
        else:
            print 'iTunes window is not found.'

## Drivers

### LDTP

A cross-platform opensource automation testing tool.

Homepage: http://ldtp.freedesktop.org/wiki/

To use ldtp driver, create UI map with

    __driver: ldtp

and describe UI elements with [LDTP naming convention](http://download.freedesktop.org/ldtp/doc/ldtp-tutorial.pdf).

### WPF

UI Automation Library provided by Microsoft with .NET Library.

Homepage: http://msdn.microsoft.com/en-us/library/ms747327.aspx

To use wpf driver, create UI map with

    __driver: wpf

and describe UI elements by properties of AutomationElement.

.NET 4.0 and IronPython required.

## Actions

### click()

Simulate user click on UI element.

### exist()

Determine whether the UI element exists.

### sendkeys(keys)

Simulate key strokes to UI element.

Example:

    ui.TXT_USERNAME.sendkeys('my_name<enter>')
    
### activate()

If the specified UI element is a window, bring it to the front, otherwise set focus to it.

Example:

    ui.WND_ITUNES.activate()
    
### maximize()

Maximize the specified window.

### value()

Get the value of the UI element.

Example:

    print 'the username is', ui.TXT_USERNAME.value()

### set_value(val)

Set the value of the UI element.

Example:

    ui.TXT_USERNAME.set_value('my_name')

### close()

Close the specified window.
