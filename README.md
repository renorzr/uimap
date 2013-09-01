# uimap

Cross platform UI Automation Python Library

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
        ui=UiMap(r'c:\itunes.yml')
        print ui.WND_ITUNES.exist()

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
